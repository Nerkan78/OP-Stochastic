# in Julia, standard arrays are indexed starting from one
# for us, in some cases it is more convinient to start indexing from zero
# this is why we use package OffsetArrays
# OrderedCollections is to be able to use the orderded set data structure 
# (to make the code deterministic so that two runs have exaclty the same result )
using Printf, OffsetArrays, OrderedCollections, LinearAlgebra, Pickle, DataFrames, CSV, IterTools, Match, Combinatorics

struct Scenario
    prob::Float64 # probability
    time::Int64   # duration of visit
    profit::Float64 # profit of visit
end

struct Label
    id::Int64
    point::Int64
    time::Int64
    profit::Float64
    prev_states::Vector{Label} # previous states
    visited_points::Vector{Int64}
end

global num_scenarios = 3

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

insert_and_dedup!(v::Vector{Label}, x::Label) = (insert!(v, searchsortedfirst(map(x -> x.time, v), x.time, rev=true), x); v)
# insert_and_dedup!(v::Vector{Label}, x::Label) = (splice!(v, searchsorted(map(x -> x.time, v), x.time, rev=true),[x]); v)


function read_data()
    
    distance = Pickle.load("data\\real\\travel_matrix.pkl")
    distance = convert(Vector{Vector{Float64}}, distance) 
    distance = mapreduce(permutedims, vcat, distance)
    distance = round.(Int, distance, RoundNearest)

    num_points=size(distance, 1) - 1

    distance = OffsetArray(distance, 0:num_points, 0 : num_points)

    profits = Pickle.load("data\\real\\profits.pkl")
    profits = convert(Vector{Float64}, profits) 

    times_distribution = Pickle.load("data\\real\\19_times_$num_scenarios.pkl")
    times_distribution = convert(Vector{Vector{Vector{Float64}}}, times_distribution) 

    rounded_times_distribution = Vector{Vector{Pair{Int64, Float64}}}()

    for point_distribution in times_distribution
        push!(rounded_times_distribution, Vector{Pair{Int64, Float64}}());
        for (firstelem, lastelem) in point_distribution
            push!(last(rounded_times_distribution), round(Int64, firstelem, RoundNearest) => round(lastelem, digits=3))
        end
    end

    # @show distance
    # @show rounded_times_distribution
    # @show profits

    horizon_length = 120
    return (distance, profits, rounded_times_distribution, horizon_length)
end

# this function extends a triple of labels (states) in the backward direction to another point
function extend_labels(labels::Vector{Label},  to_point::Int64, scenarios, cur_label_id)

    point = labels[1].point
    # first we should find the time of the extended label 
    # for this, we sort labels in the descending order of their time 
    prev_states = labels
    # visited_points = []
    visited_points = unique!(vcat(vcat(map(x -> x.visited_points, prev_states)...), [to_point]))
    sort!(prev_states, by = x -> x.time)
    # we find the maximum time of the extended label
    # which is equal to min_i{label_i.time - scenarios[point][i].time}
    time = minimum([prev_states[i].time - distance[point, to_point] - scenarios[point][i].time for i=1:num_scenarios])
    time < 0 && return nothing
    profit = sum([(prev_states[i].profit + scenarios[point][i].profit)*scenarios[point][i].prob for i=1:num_scenarios])
    return Label(cur_label_id, to_point, time, profit, prev_states, visited_points)
end

# function get_extension(labels, num_scenarios)
#     l = length(labels)
#     @match l begin
#         n::Int, if n<num_scenarios end =>  begin
#                                 extension = labels
#                                 for i in length(labels):num_scenarios-1
#                                     push!(extension, labels[end])
#                                 end
#                                 return [extension]
#                                 end
#         _ => begin
#             extensions = Vector{Label}[]
#             for i in 1:length(labels)-num_scenarios+1
#                 push!(extensions, labels[i:i+num_scenarios-1])
#             end
#             return extensions    
#         end

#     end
# end

function get_extension(labels, num_scenarios)
    l = length(labels)
    @match l begin
        n::Int, if n<num_scenarios end =>  begin
                                extension = labels
                                for i in length(labels):num_scenarios-1
                                    push!(extension, labels[end])
                                end
                                return [extension]
                                end
        _ => begin
            extensions = Vector{Label}[]
            # for i in 1:2*num_scenarios:length(labels)-2*(num_scenarios)+1
            #     for new_labels in combinations(labels[i:i+2*num_scenarios-1], num_scenarios)
            #     push!(extensions, new_labels)
            #     end
            # end
            return combinations(labels, num_scenarios)
        end

    end
end


function get_triple(labels, reference_index, num_labels)
    if reference_index == 1
       return [[labels[1] for i in 1:num_labels]]
    else
        return with_replacement_combinations(labels[1:reference_index-1], num_labels)
    end
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

function check_time(labels::Vector{Label})::Bool
    times = map(x -> x.time, labels)
    min_time = min(times...)
    new_times = map(x -> x - min_time, times)
    sort!(new_times)
    differences = new_times - possible_times
    return all(x -> abs(x) < 200, differences)
end

function get_paths_dict(label::Label, scenarios)

    #if we have only one previous state, it necessarily corresponds to returning to the depot
    if length(label.prev_states) == 1
        return Dict([0]=>1.0)
    end

    prev_point = label.prev_states[1].point

    # we merge path dictionaries of three previous states
    # when merging, we sum the probabilities for the same paths
    paths_dict = Dict{Vector{Int64}, Float64}()
    for i in 1:num_scenarios
        for (path, prob) in get_paths_dict(label.prev_states[i], scenarios)
            merge!(+, paths_dict, Dict(vcat(path,[prev_point])=>prob*scenarios[prev_point][i].prob))
        end
    end

    return paths_dict
end



function run_dynamic_programming(distance, profits, times_distribution, horizon_length)

    #num_points=size(distance, 1) - 1
    num_points = 19
    reference_points_indices = Int.(ones(num_points))
    scenarios = [[Scenario(times_distribution[point][i][2], times_distribution[point][i][1], profits[point]) for i=1:num_scenarios] for point in 2:num_points+1]

    @show scenarios
    println()
    println()
    TO_PRINT_LABELS = false

    best_label = nothing
    best_profit = -Inf64

    init_label = Label(0, 0, horizon_length, 0.0, [], [])
    cur_label_id = 1

    non_dom_labels = SetOfLabels[]
    extended_triples = Set{Triple}[]

    for point in 1:num_points
        push!(non_dom_labels, SetOfLabels())
        push!(extended_triples, Set{Triple}())
        label = Label(point, point, horizon_length - distance[0, point], 0.0, [init_label],[point])
        insert_and_dedup!(non_dom_labels[point], label)
        cur_label_id += 1
        TO_PRINT_LABELS && println("Extension (init.label) -> (p=",point, ", t=", label.time, ", prf=", label.profit, ", id = ", point, ")")
    end
    
    # we loop over the set of non-dominated labels until all triples of labels are extended 
    new_labels_were_generated = true
    number_labels_generated = 0
    num_extensions = 0
    while new_labels_were_generated 
        new_labels_were_generated = false    
        number_labels_generated = 0
        for point in 1:num_points
           
            # for labels in with_replacement_combinations(non_dom_labels[point], num_scenarios) 
            for labels in get_triple(non_dom_labels[point], reference_points_indices[point], num_scenarios-1)
                push!(labels, non_dom_labels[point][reference_points_indices[point]])
            # for labels in get_extension(non_dom_labels[point], num_scenarios)   
                # if !(map(label -> label.id, labels) in extended_triples[point]) #&& check_time([label1, label2, label3]) # label1.id <= label2.id <= label3.id <= label4.id <= label5.id && 
                    # this triple has not yet been extended, we now extend it                    
                    for to_point in 0:num_points

                        if to_point != point
                            # push!(extended_triples[point], Tuple(map(label -> label.id, labels)))
                            num_extensions += 1
    
                            new_label = extend_labels(labels, to_point, scenarios, cur_label_id)                       
    
                            #if the new label is not returned, it means that extension is not feasible
                            new_label === nothing && continue
    
                            if to_point == 0 
                                #if we come back to the depot we just check whether the new solution is the best one
                                if (new_label.profit > best_profit)
                                    best_profit = new_label.profit
                                    best_label = new_label
                                    if TO_PRINT_LABELS 
                                        print("Extension (")
                                        for (k,label) in enumerate(labels)
                                            if k > 1 
                                                print(",")
                                            end
                                            print(label.id)
                                        end
                                        println(") -> (p=", to_point, ", t=", new_label.time, ", prf=", new_label.profit, ", visited points=", new_label.visited_points, ") : new best solution")
                                    end
                                end    
                                continue
                            end

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
                            cur_label_id += 1
                            new_labels_were_generated = true
                            number_labels_generated += 1
    
                            if TO_PRINT_LABELS 
                                print("Extension (")
                                for (k,label) in enumerate(labels)
                                    if k > 1 
                                        print(",")
                                    end
                                    print(label.id)
                                end
                                print(") -> (p=", to_point, ", t=", new_label.time, ", prf=", new_label.profit, ", id=", new_label.id, ", visited points=", new_label.visited_points, ")")
                            end
                            
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
                # end
                    # end
                # end
            end
            reference_points_indices[point] += 1

        end
        println(number_labels_generated, " new labels generated")
    end 
    
    println("Number of scenarios is ", num_scenarios)
    println("Number of extensions is ", num_extensions)
    sum_non_dom_labels = 0
    for point in 1:num_points
        sum_non_dom_labels += length(non_dom_labels[point])
    end
    println("Number of created labels is ", cur_label_id)
    println("Number of non-dominated labels is ", sum_non_dom_labels)

    return (best_profit, get_paths_dict(best_label, scenarios))
    # return best_profit

end

start_time = time()

(distance, profits, times_distribution, horizon_length) = read_data()

(best_profit, paths_dict) = run_dynamic_programming(distance, profits, times_distribution, horizon_length)
# best_profit = run_dynamic_programming(distance, profits, times_distribution, horizon_length)


@printf("Best solution with profit : %.3f\n", best_profit)
global some_path
for (k, (path, prob)) in enumerate(paths_dict)
    print("Path ", k, " 0")
    for index in length(path):-1:1
        print(" -> ", path[index])
    end
    #Pickle.store("julia_path_$(num_scenarios)_$k", path)
    #Pickle.store("julia_prob_$(num_scenarios)_$k", prob)
    global some_path = path
    @printf(" with probability %.3f\n", prob)
end
println(time() - start_time)

# println(some_path)


# if num_scenarios == 1
#     global some_path = reverse(best_label.visited_points)
# end
# println(some_path)

# taken_time = time() - start_time
# global best_profits = Float64[]

# push!(best_profits, best_profit)

# global taken_times = Float64[]
# push!(taken_times, taken_time)
# global travel_time = 0
# for (node, next_node) in zip(some_path[1:end-1], some_path[2:end])
#     global travel_time += distance[node, next_node]
# end
# travel_time += distance[some_path[end], 0]

# expected_duration = sum([sum([scenarios[point][i].prob * scenarios[point][i].time  for i in 1:num_scenarios]) for point in some_path[2:end]]) + travel_time
# push!(expected_durations, expected_duration)

# # max_num_scenarios = 1
# df = DataFrame(Algorithm = ["Julia" for i in 1:max_num_scenarios],
#             Alpha = [0 for i in 1:max_num_scenarios],
#                Number_scenarios = 1:max_num_scenarios,
#                goal = best_profits,
#                taken_time = taken_times,
#                violation_probability = [0 for i in 1:max_num_scenarios],
#                expected_duration = expected_durations,
#                is_feasible = [1 for i in 1:max_num_scenarios]
#                )

# CSV.write("results_julia.csv", df, delim=';')

