//
//  EnvironmentRepository.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 9/26/20.
//

import Foundation
#if canImport(FoundationNetworking)
import OpenCombine
#else
import Combine
#endif


public class EnvironmentContainer : Repository<String, AnyObject> {
    typealias Value = ObservableObject

    public static let shared = EnvironmentContainer()

    public func store<O : AnyObject>(_ object : O, for key : String) {
        super.store(object, for: key)

        // TODO: update
    }

}
