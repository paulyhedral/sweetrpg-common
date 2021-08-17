//
//  ObjectUtilities.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 11/15/20.
//
import Foundation


public struct ObjectUtilities {

    public static func caricature(of object : Any) -> String {
        let mirror = Mirror(reflecting: object)

        let desc = "\(mirror.subjectType) {\n"
        + mirror.children.compactMap({ child in
            if let label = child.label {
                return "\t\(label): \(child.value)"
            }

            return nil
        }).joined(separator: ",\n")
        + "}"

        return desc
    }

}
