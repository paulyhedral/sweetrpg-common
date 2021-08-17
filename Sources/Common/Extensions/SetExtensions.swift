//
//  SetExtensions.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 1/13/21.
//
import Foundation


public extension Set {

    mutating func toggle(_ value : Element) {
        if self.contains(value) {
            self.remove(value)
        }
        else {
            self.insert(value)
        }
    }

}
