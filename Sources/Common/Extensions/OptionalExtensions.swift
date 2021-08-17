//
//  OptionalExtensions.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 9/26/20.
//
import Foundation


internal protocol AnyOptional {
    var isNil : Bool { get }
}

extension Optional : AnyOptional {
    public var isNil : Bool { self == nil }
}
