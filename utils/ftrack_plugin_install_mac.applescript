set home_path to home folder as alias
set target_path to alias (home_path & "Library:LaunchAgents")

tell application "Finder"
    copy POSIX file "/Volumes/jobs02/Repositories/ftrack_utils/environment.plist" to target_path
end tell