import Foundation
import Dispatch
import Foundation // for NSLock
import ServiceDiscovery
import ServiceDiscoveryHelpers
import AsyncHTTPClient
import Logging


fileprivate let logger = Logger(label: "ConsulServiceDiscovery")

/// Provides lookup for service instances that are stored in-memory.
public class ConsulServiceDiscovery<Service : Hashable, Instance : Hashable> : ServiceDiscovery {
    private let configuration : Configuration

    private let serviceInstancesLock = NSLock()
    private var serviceInstances : [Service : [Instance]]

    private let serviceSubscriptionsLock = NSLock()
    private var serviceSubscriptions : [Service : [Subscription]] = [:]

    private let queue : DispatchQueue

    public var defaultLookupTimeout : DispatchTimeInterval {
        self.configuration.defaultLookupTimeout
    }

    private let _isShutdown = SDAtomic<Bool>(false)

    public var isShutdown : Bool {
        self._isShutdown.load()
    }

    public init(configuration : Configuration, queue : DispatchQueue = .init(label: "ConsulServiceDiscovery", attributes: .concurrent)) {
        self.configuration = configuration
        self.serviceInstances = configuration.serviceInstances
        self.queue = queue
    }

    public func lookup(_ service : Service, deadline : DispatchTime? = nil, callback : @escaping (Result<[Instance], Error>) -> Void) {
        guard !self.isShutdown else {
            callback(.failure(ServiceDiscoveryError.unavailable))
            return
        }

        let isDone = SDAtomic<Bool>(false)

        let lookupWorkItem = DispatchWorkItem {
            var result : Result<[Instance], Error>! // !-safe because if-else block always set `result`
            self.serviceInstancesLock.withLock {
                if let instances = self.serviceInstances[service] {
                    result = .success(instances)
                }
                else {
                    result = .failure(LookupError.unknownService)
                }
            }

            if isDone.compareAndExchange(expected: false, desired: true) {
                callback(result)
            }
        }

        self.queue.async(execute: lookupWorkItem)

        // Timeout handler
        self.queue.asyncAfter(deadline: deadline ?? DispatchTime.now() + self.defaultLookupTimeout) {
            lookupWorkItem.cancel()

            if isDone.compareAndExchange(expected: false, desired: true) {
                callback(.failure(LookupError.timedOut))
            }
        }
    }

    @discardableResult
    public func subscribe(to service : Service, onNext nextResultHandler : @escaping (Result<[Instance], Error>) -> Void, onComplete completionHandler : @escaping (CompletionReason) -> Void = { _ in
    }) -> CancellationToken {
        guard !self.isShutdown else {
            completionHandler(.serviceDiscoveryUnavailable)
            return CancellationToken(isCancelled: true)
        }

        // Call `lookup` once and send result to subscriber
        self.lookup(service, callback: nextResultHandler)

        let cancellationToken = CancellationToken(completionHandler: completionHandler)
        let subscription = Subscription(nextResultHandler: nextResultHandler, completionHandler: completionHandler, cancellationToken: cancellationToken)

        // Save the subscription
        self.serviceSubscriptionsLock.withLock {
            var subscriptions = self.serviceSubscriptions.removeValue(forKey: service) ?? [ Subscription ]()
            subscriptions.append(subscription)
            self.serviceSubscriptions[service] = subscriptions
        }

        return cancellationToken
    }

    /// Registers a service and its `instances`.
    public func register(_ service : Service, instances : [Instance]) {
        guard !self.isShutdown else {
            return
        }

        logger.info("Registering service \(service) instances: \(instances)")

        var previousInstances : [Instance]?
        do {
            try self.serviceInstancesLock.withLock {
                previousInstances = self.serviceInstances[service]
                self.serviceInstances[service] = instances

                guard let registerUrl = URL(string: "/v1/agent/service/register", relativeTo: self.configuration.url) else {
                    throw Errors.invalidConfiguration(self.configuration.url.absoluteString)
                }
                logger.debug("Registration URL: \(registerUrl.absoluteString)")

                let httpClient = HTTPClient(eventLoopGroupProvider: .createNew)
                defer {
                    try? httpClient.syncShutdown()
                }
                var request = try HTTPClient.Request(url: registerUrl, method: .PUT)

                for instance in instances {
                    logger.debug("instance: \(instance)")

                    guard let def = instance as? ConsulServiceDefinition else {
                        logger.warning("Instance is not a ConsulServiceDefinition; skipping.")
                        continue
                    }

                    request.body = .data(try JSONEncoder().encode(def))
                    logger.debug("Executing request: \(request)...")
                    let response = try httpClient.execute(request: request)
                                             .wait()
//                              .whenComplete { result in
//                                  switch result {
//                                  case .failure(let error):
//                                      // process error
//                                      logger.error("Error while trying to PUT \(registerUrl.absoluteString): \(error)")
//                                      break
//
//                                  case .success(let response):
                                      logger.debug("Response: \(response)")
                                      if response.status == .ok {
                                          // handle response
                                          logger.info("Registration succeeded.")
                                      }
                                      else {
                                          logger.error("Unexpected response code while registering instance at \(registerUrl.absoluteString): \(response.status)")
                                          // handle remote error
                                      }
//                                  }
//                              }
                }
            }
        }
        catch {
            logger.error("Error while trying to register service instance: \(error)")
        }

        self.serviceSubscriptionsLock.withLock {
            if !self.isShutdown, instances != previousInstances, let subscriptions = self.serviceSubscriptions[service] {
                // Notify subscribers whenever instances change
                subscriptions
                        .filter {
                            !$0.cancellationToken.isCancelled
                        }
                        .forEach {
                            $0.nextResultHandler(.success(instances))
                        }
            }
        }
    }

    public func shutdown() {
        guard self._isShutdown.compareAndExchange(expected: false, desired: true) else {
            return
        }

        self.serviceSubscriptionsLock.withLock {
            self.serviceSubscriptions.values.forEach { subscriptions in
                subscriptions
                        .filter {
                            !$0.cancellationToken.isCancelled
                        }
                        .forEach {
                            $0.completionHandler(.serviceDiscoveryUnavailable)
                        }
            }
        }
    }

    private struct Subscription {
        let nextResultHandler : (Result<[Instance], Error>) -> Void
        let completionHandler : (CompletionReason) -> Void
        let cancellationToken : CancellationToken
    }
}

extension ConsulServiceDiscovery {
    public struct Configuration {
        let url : URL

        /// Default configuration
        public static var `default` : Configuration {
            .init(url: URL(string: "http://localhost:8500")!)
        }

        /// Lookup timeout in case `deadline` is not specified
        public var defaultLookupTimeout : DispatchTimeInterval = .milliseconds(100)

        internal var serviceInstances : [Service : [Instance]]

        public init(url : URL) {
            self.init(url: url, serviceInstances: [:])
        }

        /// Initializes `InMemoryServiceDiscovery` with the given service to instances mappings.
        public init(url : URL, serviceInstances : [Service : [Instance]]) {
            self.url = url
            self.serviceInstances = serviceInstances
        }

//        /// Registers `service` and its `instances`.
//        public mutating func register(service : Service, instances : [Instance]) {
//            self.serviceInstances[service] = instances
//        }
    }
}

// MARK: - NSLock extensions
extension NSLock {
    fileprivate func withLock(_ body : () throws -> Void) rethrows {
        self.lock()
        defer {
            self.unlock()
        }
        try body()
    }
}

public struct ConsulServiceDefinition : Codable, Equatable, Hashable {
    public static func ==(lhs : ConsulServiceDefinition, rhs : ConsulServiceDefinition) -> Bool {
        lhs.hashValue == rhs.hashValue
    }

    public var id : String
    public var name : String
    public var port : Int
    public var check : Check

    public init(id : String, name : String, port : Int, check : Check) {
        self.id = id
        self.name = name
        self.port = port
        self.check = check
    }

    public struct Check : Codable, Equatable, Hashable {
        public var name : String
        public var args : [String]
        public var interval : String
        public var status : String

        public init(name : String, args : [String], interval : String, status : String) {
            self.name = name
            self.args = args
            self.interval = interval
            self.status = status
        }
    }
}
