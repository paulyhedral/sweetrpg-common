//
//  Repository.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 9/26/20.
//

import Foundation


public class Repository<Key : Hashable, Value> {

    private var storage : [Key : Value] = [:]

    public init() {

    }

    public func fetch(_ key : Key) -> Value? {
        return self[key]
    }

    public func store(_ object : Value, for key : Key) {
        self[key] = object
    }

    public subscript(_ key : Key) -> Value? {
        get {
            return storage[key]
        }
        set(value) {
            storage[key] = value
        }
    }

}
