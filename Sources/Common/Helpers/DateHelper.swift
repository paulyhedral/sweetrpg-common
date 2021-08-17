//
//  DateHelper.swift
//  PilgrimageCommon
//
//  Created by Paul Schifferer on 12/16/20.
//
import Foundation


public struct DateHelper {

    private static let dateFormatter = DateFormatter()
    private static let calendar = Calendar.autoupdatingCurrent

    public static func weekdayName(for weekday : Int) -> String {

        let formatter = DateFormatter()
        formatter.dateFormat = "EEEE"

        let now = Date()
        let baseComps = calendar.dateComponents([.year, .month, .day, .weekday], from: now)

        let comps = DateComponents(calendar: Self.calendar, year: baseComps.year, month: baseComps.month, weekday: weekday, weekdayOrdinal: 1)
        if let date = calendar.date(from: comps) {
            return formatter.string(from: date)
        }

        return "⏤"
    }

}
