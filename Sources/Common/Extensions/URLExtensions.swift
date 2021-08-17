//
//  URLExtensions.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 11/7/20.
//
import Foundation


extension URL : ExpressibleByStringLiteral {

    public typealias StringLiteralType = String

    public init(stringLiteral value : StringLiteralType) {
        self.init(string: value)!
    }

}
