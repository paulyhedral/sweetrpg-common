//
// Created by Paul Schifferer on 6/16/21.
//

import Vapor
import Foundation


public final class LogRequestMiddleware : Middleware {

    public init() {
    }

    public func respond(to request : Request, chainingTo next : Responder) -> EventLoopFuture<Response> {
        let start = Date()
        return next.respond(to: request).map { response in
            self.log(response, start: start, for: request)
            return response
        }
    }

    private func log(_ response : Response, start : Date, for request : Request) {
        let reqInfo = "\(request.method.string) \(request.url.path)"
        let resInfo = "\(response.status.code) \(response.status.reasonPhrase)"
        let time = Date()
                .timeIntervalSince(start)
                .readableMilliseconds
        request.logger.info("\(reqInfo) -> \(resInfo) [\(time)]")
    }
}

extension TimeInterval {

    var readableMilliseconds : String {
        let string = (self * 1000).description
        let endIndex = string.index(string.index(of: ".")!, offsetBy: 2)
        let trimmed = string[string.startIndex..<endIndex]
        return .init(trimmed) + "ms"
    }
}
