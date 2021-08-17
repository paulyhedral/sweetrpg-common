//
//  CollectionUtilities.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 10/2/20.
//
import Foundation


extension Sequence where Iterator.Element : AnyObject {

    public func containsObjectIdentical(to object : AnyObject) -> Bool {
        return contains { $0 === object }
    }

}


extension Array {

    public var decomposed : (Iterator.Element, [Iterator.Element])? {
        guard let x = first else { return nil }
        return (x, Array(self[1..<count]))
    }

}


extension Array {

    public func safeElement(at index : Int) -> Element? {
        if index >= self.count || index < 0 {
            return nil
        }

        return self[index]
    }

}
