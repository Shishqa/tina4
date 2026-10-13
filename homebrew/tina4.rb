# Copyright (c) 2026 Code Infinity
# SPDX-License-Identifier: MPL-2.0
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

class Tina4 < Formula
  desc "Unified CLI for the Tina4 framework — Python, PHP, Ruby, Node.js"
  homepage "https://tina4.com"
  license "MPL-2.0"
  version "3.8.98"

  on_macos do
    if Hardware::CPU.arm?
      url "https://github.com/tina4stack/tina4/releases/download/v3.8.98/tina4-darwin-arm64"
      sha256 "53ad37a9156bf3b2d12ce44d142f76aca35f1611e495bc2411be148b938418e3"
    else
      url "https://github.com/tina4stack/tina4/releases/download/v3.8.98/tina4-darwin-amd64"
      sha256 "d1035b67d8a4ea5597bda96e01078194697bfb20e5ce41869c46ca8e59935198"
    end
  end

  on_linux do
    if Hardware::CPU.arm?
      url "https://github.com/tina4stack/tina4/releases/download/v3.8.98/tina4-linux-arm64"
      sha256 "5a89843b78f518f7d53d56b324188cd8b59adbfebd66766e67ba6a8eb4d6cadd"
    else
      url "https://github.com/tina4stack/tina4/releases/download/v3.8.98/tina4-linux-amd64"
      sha256 "8471026816fbd4b3458e78e41a84e88ddf96baf39380315005d76c43cb0502d7"
    end
  end

  def install
    bin.install Dir["tina4*"].first => "tina4"
  end

  test do
    assert_match "tina4", shell_output("#{bin}/tina4 --version")
  end
end
