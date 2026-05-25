import Foundation
import Vision

struct OCRLine: Encodable {
    let text: String
    let confidence: Float
}

struct OCRPayload: Encodable {
    let backend: String
    let lines: [OCRLine]
    let raw_text: String
}

enum VisionOCRError: Error {
    case missingPath
    case unreadablePath(String)
}

func main() throws {
    let args = CommandLine.arguments
    guard args.count >= 2 else {
        throw VisionOCRError.missingPath
    }

    let url = URL(fileURLWithPath: args[1])
    guard FileManager.default.fileExists(atPath: url.path) else {
        throw VisionOCRError.unreadablePath(url.path)
    }

    let request = VNRecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.usesLanguageCorrection = true
    request.recognitionLanguages = ["zh-Hans", "en-US"]

    let handler = VNImageRequestHandler(url: url, options: [:])
    try handler.perform([request])

    let observations = (request.results ?? []).sorted { lhs, rhs in
        let leftTop = lhs.boundingBox.maxY
        let rightTop = rhs.boundingBox.maxY
        if leftTop == rightTop {
            return lhs.boundingBox.minX < rhs.boundingBox.minX
        }
        return leftTop > rightTop
    }

    let lines = observations.compactMap { observation -> OCRLine? in
        guard let candidate = observation.topCandidates(1).first else {
            return nil
        }
        let text = candidate.string.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else {
            return nil
        }
        return OCRLine(text: text, confidence: candidate.confidence)
    }

    let payload = OCRPayload(
        backend: "vision_swift",
        lines: lines,
        raw_text: lines.map(\.text).joined(separator: "\n")
    )
    let encoder = JSONEncoder()
    let data = try encoder.encode(payload)
    FileHandle.standardOutput.write(data)
}

do {
    try main()
} catch VisionOCRError.missingPath {
    FileHandle.standardError.write(Data("missing image path\n".utf8))
    exit(2)
} catch VisionOCRError.unreadablePath(let path) {
    FileHandle.standardError.write(Data("image not found: \(path)\n".utf8))
    exit(2)
} catch {
    FileHandle.standardError.write(Data("\(error)\n".utf8))
    exit(1)
}
