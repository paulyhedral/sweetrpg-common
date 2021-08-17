//
//  BoolExtensions.swift
//
//
//  Created by Paul Schifferer on 11/6/20.
//
import Foundation


public extension Bool {

    func predicateValue() -> String {
        switch self {
        case false:
            return "NO"

        case true:
            return "YES"
        }
    }

}
