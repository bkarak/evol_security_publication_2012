#!/usr/bin/env ruby

require 'json'
require 'zlib'

file  = ARGV[0]       || fail("No file to parse")
ts    = ARGV[1].to_i  || fail("No timestamp to construct graph at")

puts "Reading file #{file}"
puts "Using timestamp filter #{Time.at(ts)}"

f = File.open(file)
gz = Zlib::GzipReader.new(f).read
js = JSON.parse(gz)

#js.each{|e| e[1]['timestamp'] = rand(1044347625..1359966825)}
js.each{|e| e[1]['timestamp'] = e[1]['timestamp'].to_i}

processed = 0
subgraph = js.reduce([]) { |acc, e|
  STDERR.print "\rProcessed #{processed += 1} nodes"
  if e[1]['timestamp'] < ts
    acc << e
  end
  acc
}

STDERR.puts
STDERR.puts "Reduced to #{subgraph.size} nodes"

#def dfs(graph, deps)
#  deps.map{|d| }
#end
#
#subgraph.each { |x|
#  x[1]['dependencies '].map{ |d|
#    dep = subgraph.find{|e| e[0] == d}
#    "#{x[0]} -> #{dep[0]}"
#  }
#}

