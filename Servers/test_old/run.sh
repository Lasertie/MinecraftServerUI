#!/usr/bin/env sh
# Add custom JVM arguments (such as RAM allocation) to the user_jvm_args.txt

java -jar forge-1.21.1-52.0.2-shim.jar --onlyCheckJava || exit 1

# Add custom program arguments (such as nogui) to the next line before the "$@" or pass them to this script directly
java @user_jvm_args.txt @libraries/net/minecraftforge/forge/1.21.1-52.0.2/unix_args.txt "$@"
