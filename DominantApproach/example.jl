# in Julia, standard arrays are indexed starting from one
# for us, in some cases it is more convinient to start indexing from zero
# this is why we use package OffsetArrays
# OrderedCollections is to be able to use the orderded set data structure 
# (to make the code deterministic so that two runs have exaclty the same result )
using OffsetArrays, OrderedCollections

# Scenario structure
struct Scenario
    prob::Float64 # probability
    time::Int64   # duration of visit
    profit::Int64 # profit of visit
end

# the data consists of 
# - a number of points with ids from 1 to num_points
# - the depot (starting and finished point) has id 0
# - distance matrix between point (indexing starts from 0)
# - matrix of scenarios for all (non-depot) points 
#   each point has three scenarios
#   scenarios for the same point should be sorted by non-increasing of the time
    

# data for the instance with three (non-depot) points

num_points = 3
distance = OffsetArray(Int64[0 2 3 4; 
                             2 0 2 4; 
                             3 2 0 1; 
                             4 4 1 0], 
                       0:num_points, 0:num_points)
scenarios = Scenario[Scenario(1, 4, 10); Scenario(1, 2, 3); Scenario(1, 0, 0)]
  

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
struct Label
    id::Int64
    point::Int64
    time::Int64
    profit::Float64
    prev_states::Vector{Label} # previous states
end

TO_PRINT_LABELS = true

# const Triple = Tuple{Int64}
const SetOfLabels = OrderedSet{Label}

horizon_length = 16
init_label = Label(0, 0, horizon_length, 0.0, [])
cur_label_id = 1

non_dom_labels = SetOfLabels[]
extended_triples = Set{Int64}[]

for point in 1:num_points
    push!(non_dom_labels, SetOfLabels())
    push!(extended_triples, Set{Int64}())
    label = Label(point, point, horizon_length - distance[0, point], 0.0, [init_label])
    push!(non_dom_labels[point], label)
    global cur_label_id += 1
    TO_PRINT_LABELS && println("Extension (0,0,0) -> (p=",point, ",t=", label.time, ",prf=", label.profit, ",id = ", point, ")")
end

best_label = nothing
best_profit = -Inf64

# this function extends a triple of labels (states) in the backward direction to another point
function extend_labels(label1, to_point::Int64)
    point = label1.point
    # first we should find the time of the extended label 
    # for this, we sort labels in the descending order of their time 
    prev_states = [label1]
    sort!(prev_states, by = x -> x.time, rev = true)
    # we find the maximum time of the extended label
    # which is equal to min_i{label_i.time - scenarios[point, i].time}
    time = minimum([prev_states[i].time - distance[point, to_point] - scenarios[point, i].time for i=1:1])
    time < 0 && return nothing
    profit = sum([(prev_states[i].profit + scenarios[point, i].profit)*scenarios[point, i].prob for i=1:1])
    return Label(cur_label_id, to_point, time, profit, prev_states)
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
new_labels_were_generated = true
num_extensions = 0
while new_labels_were_generated 
    global new_labels_were_generated = false    
    for point in 1:num_points
        # we loop over all ordered triples of labels for this point
        for label1 in non_dom_labels[point]
            if !(label1.id in extended_triples[point])
               # this triple has not yet been extended, we now extend it
               for to_point in 0:num_points
                    if to_point != point
                        push!(extended_triples[point], label1.id)
                        global num_extensions += 1

                        new_label = extend_labels(label1, to_point)                       

                        #if the new label is not returned, it means that extension is not feasible
                        new_label === nothing && continue

                        if to_point == 0 
                            #if we come back to the depot we just check whether the new solution is the best one
                            if (new_label.profit > best_profit)
                                global best_profit = new_label.profit
                                global best_label = new_label
                                TO_PRINT_LABELS && println("Extension (", label1.id, ") -> (t=", 
                                                           new_label.time, ",", "prf=", new_label.profit, ") : new best solution")
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
                                delete!(non_dom_labels[to_point], ex_label)
                            end
                        end

                        # we add the new label to the set of non-dominated labels
                        push!(non_dom_labels[to_point], new_label)
                        global cur_label_id += 1
                        global new_labels_were_generated = true

                        TO_PRINT_LABELS && print("Extension (", label1.id, ") -> (p=", to_point, 
                                                 ",t=", new_label.time, ",", "prf=", new_label.profit, ",id=", new_label.id, ")")
                        
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
        end
    end
end
println("Length of prev states ", best_label.prev_states)
#we now print the solution stored in the best label
function get_paths_dict(label::Label)

    # if num_scenarios == 1

    #if we have only one previous state, it necessarily corresponds to returning to the depot
    if length(label.prev_states) == 1
        return Dict([0]=>1.0)
    end

    prev_point = label.prev_states[1].point
    println("GO INSIDE")
    # we merge path dictionaries of three previous states
    # when merging, we sum the probabilities for the same paths
    paths_dict = Dict{Vector{Int64}, Float64}()
    for i in 1:1
        for (path, prob) in get_paths_dict(label.prev_states[i])
            merge!(+, paths_dict, Dict(vcat(path,[prev_point])=>prob*scenarios[prev_point, i].prob))
        end
    end

    return paths_dict
end

println(get_paths_dict(best_label))
println("Best solution with profit : ", best_profit)
for (path, prob) in get_paths_dict(best_label)
    print("Path 0")
    for index in length(path):-1:1
        print(" -> ", path[index])
    end
    println(" with probability ", prob)
end
println("Number of extensions is ", num_extensions)
sum_non_dom_labels = 0
for point in 1:num_points
    global sum_non_dom_labels += length(non_dom_labels[point])
end
println("Number of created labels is ", cur_label_id)
println("Number of non-dominated labels is ", sum_non_dom_labels)

