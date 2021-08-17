//
//  SequenceExtensions.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 1/22/21.
//
import Foundation


public extension Sequence {

    func sorted<T : Comparable>(by keyPath : KeyPath<Element, T>) -> [Element] {
        sorted { a, b in
            a[keyPath: keyPath] < b[keyPath: keyPath]
        }
    }

    func elements(at indexSet : IndexSet) -> [Element] {
        return self.enumerated().filter { indexSet.contains($0.0) }.map { $0.1 }
    }

}
