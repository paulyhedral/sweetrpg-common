import Foundation


public enum Errors : Error {
    case missingConfiguration(String)
    case invalidConfiguration(String)
}
