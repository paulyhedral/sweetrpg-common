//
// Created by Paul Schifferer on 6/24/21.
//

import Foundation
import Vapor


public struct ConsulServiceRegistryUtils {
    public static func register(instanceName : String, serviceName : String, application : Application) throws {
        guard let serviceDiscoveryUrlString = Environment.get(.serviceDiscoveryURLKey),
              let serviceDiscoveryUrl = URL(string: serviceDiscoveryUrlString) else {
            fatalError("\(String.serviceDiscoveryURLKey) missing or invalid: \(String(describing: Environment.get(.serviceDiscoveryURLKey)))")
        }
        application.logger.debug("\(String.serviceDiscoveryURLKey): \(serviceDiscoveryUrl.absoluteString)")

        guard let portValue = Environment.get("PORT"), let port = Int(portValue), port > 0 else {
            fatalError("PORT value missing or invalid: \(String(describing: Environment.get("PORT")))")
        }
        guard let checkURLString = Environment.get(.serviceCheckURLKey), let checkURL = URL(string: checkURLString) else {
            fatalError("\(String.serviceCheckURLKey) value missing or invalid: \(String(describing: Environment.get(.serviceCheckURLKey)))")
        }
        // get hostname
        let hostname = Host.current().localizedName ?? "localhost"

        let sdConfig = ConsulServiceDiscovery<String, ConsulServiceDefinition<HTTPServiceCheck>>.Configuration(url: serviceDiscoveryUrl)
        let nodeMeta = ConsulServiceNodeMeta(externalNode: "true", externalProbe: "true")
        let service = ConsulServiceDetail(id: instanceName, service: serviceName, port: port)
        let thisInstance = ConsulServiceDefinition<HTTPServiceCheck>(node: hostname,
                address: hostname,
                nodeMeta: nodeMeta,
                service: service,
                checks: [
                    HTTPServiceCheck(name: "http check", status: "passing",
                            definition: HTTPCheckDefinition(id: "http", name: "http check",
                                    http: checkURL,
                                    body: "",
                                    interval: "30s",
                                    timeout: "5s"))
                ])
        ConsulServiceDiscovery(configuration: sdConfig).register(serviceName, instances: [ thisInstance ])
    }
}
