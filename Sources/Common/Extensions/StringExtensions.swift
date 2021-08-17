//
//  StringExtensions.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 11/17/20.
//
import Foundation


public extension String {

    func capitalizingFirstLetter() -> String {
        return prefix(1).capitalized + dropFirst()
    }

    mutating func capitalizeFirstLetter() {
        self = self.capitalizingFirstLetter()
    }

    func lines(separator : Character = "\r") -> [String] {
        self.split(separator: separator).map { String($0) }
    }

}
