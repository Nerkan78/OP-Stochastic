# in Julia, standard arrays are indexed starting from one
# for us, in some cases it is more convinient to start indexing from zero
# this is why we use package OffsetArrays
# OrderedCollections is to be able to use the orderded set data structure 
# (to make the code deterministic so that two runs have exaclty the same result )
using OffsetArrays, OrderedCollections, LinearAlgebra, Pickle, DataFrames, CSV, IterTools, Match, Combinatorics

struct Scenario
    prob::Float64 # probability
    time::Float64   # duration of visit
    profit::Float64 # profit of visit
end

struct Label
    id::Int64
    point::Int64
    time::Float64
    profit::Float64
    prev_states::Vector{Label} # previous states
    visited_points::Vector{Int64}
end
# const Triple = Tuple{Int64, Int64, Int64}

# const SetOfLabels = Vector{Label}


global best_profits = Float64[]
global expected_durations = Float64[]
global taken_times = Float64[]
global cur_label_id
global max_num_scenarios = 5


for num_scenarios in 1:5

Triple = @match num_scenarios begin
    1 => Tuple{Int64}
    2 => Tuple{Int64, Int64}
    3 => Tuple{Int64, Int64, Int64}
    4 => Tuple{Int64, Int64, Int64, Int64}
    5 => Tuple{Int64, Int64, Int64, Int64, Int64}
    6 => Tuple{Int64, Int64, Int64, Int64, Int64, Int64}
    7 => Tuple{Int64, Int64, Int64, Int64, Int64, Int64, Int64}
    8 => Tuple{Int64, Int64, Int64, Int64, Int64, Int64, Int64, Int64}
end
SetOfLabels = Vector{Label}

start_time = time()
# Scenario structure


# the data consists of 
# - a number of points with ids from 1 to num_points
# - the depot (starting and finished point) has id 0
# - distance matrix between point (indexing starts from 0)
# - matrix of scenarios for all (non-depot) points 
#   each point has three scenarios
#   scenarios for the same point should be sorted by non-increasing of the time
    

# data for the instance with three (non-depot) points


# a = Pickle.load("times_2.pkl")
# a = convert(Vector{Vector{Vector{Float64}}}, a) 
# println(a)
# num_points = 19
# distance = rand(Float64, (num_points + 1, num_points + 1)) 
# distance = distance' * distance * 0.5
# distance[diagind(distance)] .= 0
# distance = OffsetArray(distance, 0:num_points, 0 : num_points)
# display(distance)
# possible_times = [5, 10, 15]#, 150, 180]

# profits = rand(1:4, num_points)
# scenarios = [[Scenario(1 / 3, possible_times[i], profits[point]) for i=1:3] for point in 1:num_points]


times_distribution = Pickle.load("times_$num_scenarios.pkl")
times_distribution = convert(Vector{Vector{Vector{Float64}}}, times_distribution) 

distance = Pickle.load("travel_matrix.pkl")
distance = convert(Vector{Vector{Float64}}, distance) 
num_points=size(distance, 1) -1
distance = mapreduce(permutedims, vcat, distance)
distance = OffsetArray(distance, 0:num_points, 0 : num_points)

profits = Pickle.load("profits.pkl")
profits = convert(Vector{Float64}, profits) 

scenarios = [[Scenario(times_distribution[point][i][2], times_distribution[point][i][1], profits[point]) for i=1:num_scenarios] for point in 2:num_points+1]
# scenarios = Scenario[]


# for point in 1:num_points
#     profit = rand(1:4)
#     new_scenario = [Scenario(1 / 3, possible_times[i], profit) for i=1:3]
#     append!(scenarios, new_scenario)
    
# end
# scenarios = reshape(scenarios, (num_points,3))

# num_points = 3
# distance = OffsetArray(Int64[0 2 3 4; 
#                              2 0 2 4; 
#                              3 2 0 1; 
#                              4 4 1 0], 
#                        0:num_points, 0:num_points)
# scenarios = Scenario[Scenario(0.5, 4, 10) Scenario(0.4, 2, 3) Scenario(0.1, 0, 0); 
#                      Scenario(0.7, 3, 7)  Scenario(0.1, 2, 4) Scenario(0.2, 1, 1);
#                      Scenario(0.3, 5, 11) Scenario(0.6, 2, 4) Scenario(0.1, 0, 0)]


# data for the instance with four (non-depot) points

# num_points = 4
# distance = OffsetArray(Int64[0 2 3 4 3; 
#                              2 0 2 4 1; 
#                              3 2 0 1 1; 
#                              4 4 1 0 2;
#                              3 1 1 2 0], 
#                         0:num_points, 0:num_points)
# scenarios = Scenario[Scenario(0.5, 4, 10) Scenario(0.4, 2, 3) Scenario(0.1, 0, 0); 
#                      Scenario(0.7, 3, 7)  Scenario(0.1, 2, 4) Scenario(0.2, 1, 1);
#                      Scenario(0.3, 5, 11) Scenario(0.6, 2, 4) Scenario(0.1, 0, 0);
#                      Scenario(0.4, 4, 8)  Scenario(0.4, 3, 6)  Scenario(0.2, 1, 2)]


# Label structure
# each label corresponds to an MDP state which can be reached from the depot in the backward direction




function check_time(labels::Vector{Label})::Bool
    times = map(x -> x.time, labels)
    min_time = min(times...)
    new_times = map(x -> x - min_time, times)
    sort!(new_times)
    differences = new_times - possible_times
    return all(x -> abs(x) < 200, differences)
end

TO_PRINT_LABELS = false
insert_and_dedup!(v::Vector{Label}, x::Label) = (splice!(v, searchsorted(map(x -> x.id, v), x.id), [x]); v)

# const Triple = Tuple{Int64, Int64, Int64, Int64, Int64}


horizon_length = 120
init_label = Label(0, 0, horizon_length, 0.0, [], [])
global cur_label_id = 1

non_dom_labels = SetOfLabels[]
extended_triples = Set{Triple}[]

for point in 1:num_points
    push!(non_dom_labels, SetOfLabels())
    push!(extended_triples, Set{Triple}())
    label = Label(point, point, horizon_length - distance[0, point], 0.0, [init_label],[point])
    insert_and_dedup!(non_dom_labels[point], label)
    global cur_label_id += 1
    TO_PRINT_LABELS && println("Extension (0,0,0) -> (p=",point, ",t=", label.time, ",prf=", label.profit, ",id = ", point, ")")
end

global best_label = nothing
global best_profit = -Inf64

# this function extends a triple of labels (states) in the backward direction to another point
# function extend_labels(label1::Label, label2::Label, label3::Label, label4::Label, label5::Label,  to_point::Int64)
function extend_labels(labels::Vector{Label},  to_point::Int64)

    point = labels[1].point
    # first we should find the time of the extended label 
    # for this, we sort labels in the descending order of their time 
    prev_states = labels
    # visited_points = []
    visited_points = unique!(vcat(vcat(map(x -> x.visited_points, prev_states)...), [to_point]))
    sort!(prev_states, by = x -> x.time, rev = true)
    # we find the maximum time of the extended label
    # which is equal to min_i{label_i.time - scenarios[point][i].time}
    time = minimum([prev_states[i].time - distance[point, to_point] - scenarios[point][i].time for i=1:num_scenarios])
    time < 0 && return nothing
    profit = sum([(prev_states[i].profit + scenarios[point][i].profit)*scenarios[point][i].prob for i=1:num_scenarios])
    return Label(cur_label_id, to_point, time, profit, prev_states, visited_points)
end

# this function checks whether label1 dominates label2
function dominates(label1::Label, label2::Label)::Bool
    label1.point != label2.point && return false

    label1.time < label2.time && return false
    label1.profit < label2.profit && return false
    label1.time > label2.time && return true
    label1.profit > label2.profit && return true
    return label1.id < label2.id
end

function print_non_dominated_label_ids()
    for point in 1:num_points
        print("Point ", point, " :")
        for label in non_dom_labels[point]
            print(" ", label.id)
        end
        println()
    end
end

# we loop over the set of non-dominated labels until all triples of labels are extended 
global new_labels_were_generated = true
global number_labels_generated = 0
global num_extensions = 0
while new_labels_were_generated 
    global new_labels_were_generated = false    
    global number_labels_generated = 0
    for point in 1:num_points
        println("point ", point)
        # we loop over all ordered triples of labels for this point
        add = 0
        # for (idx1, label1) in enumerate(non_dom_labels[point])
        #     # add = if length(non_dom_labels[point]) < 3 0 else 1 end
        #     for (idx2, label2) in enumerate(non_dom_labels[point][idx1+add:end])
        #         # add = if length(non_dom_labels[point]) < 2 0 else 1 end
        #         for (idx3, label3) in enumerate(non_dom_labels[point][idx2+add:end])   
    
        for labels in with_replacement_combinations(non_dom_labels[point], num_scenarios)    
            # println(labels)        
            if !(map(label -> label.id, labels) in extended_triples[point]) #&& check_time([label1, label2, label3]) # label1.id <= label2.id <= label3.id <= label4.id <= label5.id && 
                # this triple has not yet been extended, we now extend it
                for to_point in 0:num_points
                    if to_point in mapreduce(label -> label.visited_points, vcat, labels)
                        continue
                    end
                    # if to_point in label2.visited_points
                    #     continue
                    # end
                    # if to_point in label3.visited_points
                    #     continue
                    # end
                
                    if to_point != point
                        push!(extended_triples[point], Tuple(map(label -> label.id, labels)))
                        global num_extensions += 1

                        new_label = extend_labels(labels, to_point)                       

                        #if the new label is not returned, it means that extension is not feasible
                        new_label === nothing && continue

                        if to_point == 0 
                            #if we come back to the depot we just check whether the new solution is the best one
                            if (new_label.profit > best_profit)
                                global best_profit = new_label.profit
                                global best_label = new_label
                                TO_PRINT_LABELS && println("Extension (", label1.id, ",", label2.id, ",", label3.id,  ") -> (t=", 
                                                        new_label.time, ",", "prf=", new_label.profit, "visited points=", new_label.visited_points, ") : new best solution")
                            end    
                            continue
                        else
                            #if we are in an intermediate point, we check whether the new label is dominated    
                            new_label_is_dominated = false
                            for ex_label in non_dom_labels[to_point]
                                if dominates(ex_label, new_label) 
                                    new_label_is_dominated = true
                                    break
                                end
                            end    
                            #if it is dominated, we do not keep it
                            new_label_is_dominated && continue
                        end

                        dom_label_ids = Int64[]

                        # at this point we know that the new label is non-dominated
                        # we now check whether the new label dominates other labels
                        for ex_label in non_dom_labels[to_point]
                            if dominates(new_label, ex_label) 
                                # we delete dominated labels
                                push!(dom_label_ids, ex_label.id)
                                filter!(x -> x.id != ex_label.id, non_dom_labels[to_point])
                                #delete!(non_dom_labels[to_point], ex_label)
                            end
                        end

                        # we add the new label to the set of non-dominated labels
                        insert_and_dedup!(non_dom_labels[to_point], new_label)
                        global cur_label_id += 1
                        global new_labels_were_generated = true
                        global number_labels_generated += 1

                        TO_PRINT_LABELS && print("Extension (", label1.id, ",", label2.id, ",", label3.id, ") -> (p=", to_point, 
                                                ",t=", new_label.time, ",", "prf=", new_label.profit, ",id=", new_label.id, "visited points=", new_label.visited_points, ")")
                        
                        if TO_PRINT_LABELS && !isempty(dom_label_ids)
                            print(", dominates labels")
                            for id in dom_label_ids
                                print(" ", id)    
                            end
                        end

                        TO_PRINT_LABELS && println()
                        # if mod(cur_label_id, 10) == 0
                        #     print_non_dominated_label_ids()
                        # end
                    end
                        
                end
            end
                # end
            # end
        end
    end
    println(number_labels_generated)
end

#we now print the solution stored in the best label
function get_paths_dict(label::Label)

    #if we have only one previous state, it necessarily corresponds to returning to the depot
    if length(label.prev_states) == 1
        return Dict([0]=>1.0)
    end

    prev_point = label.prev_states[1].point

    # we merge path dictionaries of three previous states
    # when merging, we sum the probabilities for the same paths
    paths_dict = Dict{Vector{Int64}, Float64}()
    for i in 1:num_scenarios
        for (path, prob) in get_paths_dict(label.prev_states[i])
            merge!(+, paths_dict, Dict(vcat(path,[prev_point])=>prob*scenarios[prev_point][i].prob))
        end
    end

    return paths_dict
end

println("Best solution with profit : ", best_profit)
global some_path
for (k, (path, prob)) in enumerate(get_paths_dict(best_label))
    print("Path 0")
    for index in length(path):-1:1
        print(" -> ", path[index])
    end
    Pickle.store("julia_path_$(num_scenarios)_$k", path)
    Pickle.store("julia_prob_$(num_scenarios)_$k", prob)
    global some_path = path
    println(" with probability ", prob)
end
println(some_path)
println("Number of extensions is ", num_extensions)
global sum_non_dom_labels = 0
for point in 1:num_points
    global sum_non_dom_labels += length(non_dom_labels[point])
end
println("Number of created labels is ", cur_label_id)
println("Number of non-dominated labels is ", sum_non_dom_labels)


if num_scenarios == 1
    global some_path = reverse(best_label.visited_points)
end
println(some_path)
taken_time = time() - start_time
push!(best_profits, best_profit)
push!(taken_times, taken_time)
global travel_time = 0
for (node, next_node) in zip(some_path[1:end-1], some_path[2:end])
    travel_time += distance[node, next_node]
end
travel_time += distance[some_path[end], 0]
expected_duration = sum([sum([scenarios[point][i].prob * scenarios[point][i].time  for i in 1:num_scenarios]) for point in some_path[2:end]]) + travel_time
push!(expected_durations, expected_duration)

end
# max_num_scenarios = 1
df = DataFrame(Algorithm = ["Julia" for i in 1:max_num_scenarios],
            Alpha = [0 for i in 1:max_num_scenarios],
               Number_scenarios = 1:max_num_scenarios,
               goal = best_profits,
               taken_time = taken_times,
               violation_probability = [0 for i in 1:max_num_scenarios],
               expected_duration = expected_durations,
               is_feasible = [1 for i in 1:max_num_scenarios]
               )

CSV.write("results_julia.csv", df, delim=';')

