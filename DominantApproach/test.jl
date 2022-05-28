using Match
c = @match 5 begin
    n::Int               => 2
    str::String          => 3
    m::Dict{Int, String} => 4
    d::Dict              => println("A Dict! Looking up a word?")
    _                    => println("Something unexpected")
end

println(c)
