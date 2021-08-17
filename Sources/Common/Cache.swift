//
//  Cache.swift
//  PilgrimageCommon
//  With thanks to John Sundell.
//  https://www.swiftbysundell.com/articles/caching-in-swift/
//
//  Created by Paul Schifferer on 10/14/20.
//

import Foundation
import Logging


fileprivate let logger = Logger(label: Constants.logPrefix+"cache")

public final class Cache<Key : Hashable, Value> {

    private let wrapped = NSCache<WrappedKey, Entry>()
    private let dateProvider : () -> Date
    private let entryLifetime : TimeInterval
    private let keyTracker = KeyTracker()

    public init(dateProvider : @escaping () -> Date = Date.init,
         entryLifetime : TimeInterval = 12 * 60 * 60,
         maximumEntryCount : Int = 50) {
        self.dateProvider = dateProvider
        self.entryLifetime = entryLifetime
        wrapped.countLimit = maximumEntryCount
        wrapped.delegate = keyTracker
    }

    public func insert(_ value : Value, forKey key : Key) {
        logger.info("\(#function); key: \(key); value: \(value)")

        let date = dateProvider().addingTimeInterval(entryLifetime)
        let entry = Entry(key: key, value: value, expirationDate: date)
        wrapped.setObject(entry, forKey: WrappedKey(key))
        keyTracker.keys.insert(key)
    }

    public func value(forKey key : Key) -> Value? {
        guard let entry = wrapped.object(forKey: WrappedKey(key)) else {
            return nil
        }

        guard dateProvider() < entry.expirationDate else {
            // Discard values that have expired
            removeValue(forKey: key)
            return nil
        }

        return entry.value
    }

    public func removeValue(forKey key : Key) {
        wrapped.removeObject(forKey: WrappedKey(key))
    }

    //    public var defaultTimeout : TimeInterval = 1000
    //
    //    public func insert(_ value : Value, forKey key : Key, timeout : TimeInterval? = nil) {
    //        let timeout = timeout ?? defaultTimeout
    //        let expirationDate = Date().addingTimeInterval(timeout)
    //
    //        values[key] = Container(
    //            value: value,
    //            date: expirationDate
    //        )
    //    }
    //
    //    public func value(forKey key : Key) -> Value? {
    //        guard let container = values[key] else {
    //            return nil
    //        }
    //
    //        // If the container's date is in the past, then the
    //        // value has expired, and we remove it from the cache.
    //        guard container.date > Date() else {
    //            values[key] = nil
    //            return nil
    //        }
    //
    //        return container.value
    //    }
}

private extension Cache {

    final class WrappedKey : NSObject {
        let key : Key

        init(_ key : Key) { self.key = key }

        override var hash : Int { return key.hashValue }

        override func isEqual(_ object : Any?) -> Bool {
            guard let value = object as? WrappedKey else {
                return false
            }

            return value.key == key
        }
    }

    final class Entry {
        let key: Key
        let value: Value
        let expirationDate: Date

        init(key : Key, value : Value, expirationDate : Date) {
            self.key = key
            self.value = value
            self.expirationDate = expirationDate
        }
    }

    final class KeyTracker : NSObject, NSCacheDelegate {
        var keys = Set<Key>()

        func cache(_ cache: NSCache<AnyObject, AnyObject>,
                   willEvictObject object: Any) {
            guard let entry = object as? Entry else {
                return
            }

            keys.remove(entry.key)
        }
    }

    func entry(forKey key : Key) -> Entry? {
        guard let entry = wrapped.object(forKey: WrappedKey(key)) else {
            return nil
        }

        guard dateProvider() < entry.expirationDate else {
            removeValue(forKey: key)
            return nil
        }

        return entry
    }

    func insert(_ entry : Entry) {
        wrapped.setObject(entry, forKey: WrappedKey(entry.key))
        keyTracker.keys.insert(entry.key)
    }

}

public extension Cache {

    subscript(key: Key) -> Value? {
        get { return value(forKey: key) }
        set {
            guard let value = newValue else {
                // If nil was assigned using our subscript,
                // then we remove any value for that key:
                removeValue(forKey: key)
                return
            }

            insert(value, forKey: key)
        }
    }

}

extension Cache.Entry : Codable where Key : Codable, Value : Codable {}

extension Cache : Codable where Key : Codable, Value : Codable {

    public convenience init(from decoder : Decoder) throws {
        self.init()

        let container = try decoder.singleValueContainer()
        let entries = try container.decode([Entry].self)
        entries.forEach(insert)
    }

    public func encode(to encoder : Encoder) throws {
        var container = encoder.singleValueContainer()
        try container.encode(keyTracker.keys.compactMap(entry))
    }

}

extension Cache where Key : Codable, Value : Codable {

    public func saveToDisk(withName name : String, using fileManager : FileManager = .default) throws {
        let folderURLs = fileManager.urls(for: .cachesDirectory,
            in: .userDomainMask)

        let fileURL = folderURLs[0].appendingPathComponent(name + ".cache")
        let data = try JSONEncoder().encode(self)
        try data.write(to: fileURL)
    }

}
