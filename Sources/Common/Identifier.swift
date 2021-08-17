//
//  Identifier.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 9/12/20.
//
import Foundation


/**
 A useful identifier type for model types.
 */
public struct Identifier<V : Identifiable, T : Hashable> : Hashable {
    public var identifier : T

    public init(identifier : T) {
        self.identifier = identifier
    }
}


//extension Identifier : ExpressibleByStringLiteral where T == String {
//
//    public init(stringLiteral value : String) {
//        identifier = value
//    }
//
//}

extension Identifier : CustomStringConvertible where T == String {

    public var description : String {
        return identifier
    }

}


extension Identifier : Codable where T == String {

    public init(from decoder : Decoder) throws {
        let container = try decoder.singleValueContainer()
        identifier = try container.decode(String.self)
    }

    public func encode(to encoder : Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(identifier)
    }

}


//public struct AnyIdentifier : Identifiable {
//    public var id : Identifier<String, String>
//}
