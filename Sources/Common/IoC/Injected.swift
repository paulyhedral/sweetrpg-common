//
//  EnvironmentObject.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 9/26/20.
//
import Foundation
#if canImport(OpenCombine)
import OpenCombine
#else
import Combine
#endif


@propertyWrapper
public struct Injected<Value : AnyObject> {
    private let key : String

    public init(_ key : String) {
        self.key = key

        if let obj = EnvironmentContainer.shared[key] as? Value {
            self.wrappedValue = obj
        }
        //        else {
        //            self.wrappedValue = nil
        //        }
    }

    public var wrappedValue : Value {
        get {
            return EnvironmentContainer.shared[key] as! Value
        }
        set {
            if let optional = newValue as? AnyOptional, optional.isNil {
                EnvironmentContainer.shared[key] = nil
            } else {
                EnvironmentContainer.shared[key] = newValue
            }
        }
    }

//    public var projectedValue : EnvironmentObject { self }
}
