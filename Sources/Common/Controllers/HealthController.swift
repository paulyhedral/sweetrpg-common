//
// HealthController.swift
// Copyright (c) 2021 Paul Schifferer.
//

import Vapor


public struct HealthController<H : HealthInfo> : RouteCollection {

    // health check callback function
    private let healthCallback : () -> H

    public init(healthCallback : @escaping () -> H) {
        self.healthCallback = healthCallback
    }

    public func boot(routes : RoutesBuilder) throws {
        let healthRoutes = routes.grouped("health")
        healthRoutes.get("status", use: self.healthCheckHandler)
        healthRoutes.get("ping", use: self.pingHandler)
    }

    func healthCheckHandler(_ req : Request) throws -> EventLoopFuture<H> {
        let info = healthCallback()
        return req.eventLoop.future(info)
    }

    func pingHandler(_ req : Request) throws -> EventLoopFuture<Pong> {
        let pong = Pong(timestamp: Date())
        return req.eventLoop.future(pong)
    }
}

public protocol HealthInfo : Content {}

public struct BasicHealthInfo : HealthInfo {
    public let timestamp : Date

    public init(timestamp : Date = Date()) {
        self.timestamp = timestamp
    }
}

struct Pong : Content {
    let timestamp : Date
}
