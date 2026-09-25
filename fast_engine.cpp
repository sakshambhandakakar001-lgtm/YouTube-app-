#include <iostream>
#include <string>

extern "C" {
    const char* resolve_video_path_cpp(const char* input_path) {
        std::string path(input_path);
        if (path.find(".mp4") != std::string::npos || path.find(".mkv") != std::string::npos) {
            return input_path;
        }
        return "default.mp4";
    }
}
