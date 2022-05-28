module utils
export Scenario, Label, TripleLabel, check_time, Triple, SetOfLabels, LabelTriples, extend_labels, dominates, print_non_dominated_label_ids, get_paths_dict
# using DelimitedFiles
# using OffsetArrays, OrderedCollections, LinearAlgebra

struct Scenario
    prob::Float64 # probability
    time::Int64   # duration of visit
    profit::Int64 # profit of visit
end



struct Label
    id::Int64
    point::Int64
    time::Float64
    profit::Float64
    prev_states::Vector{Label} # previous states
    visited_points::Vector{Int64}
end

struct TripleLabel
    id :: Int64
    labels :: Vector{Label}
    extended_label :: Label
end

insert_and_dedup!(v::Vector{Label}, x::Label) = (splice!(v, searchsorted(map(x -> x.id, v), x.id), [x]); v)


function check_time(labels::Vector{Label})::Bool
    times = map(x -> x.time, labels)
    min_time = min(times...)
    new_times = map(x -> x - min_time, times)
    sort!(new_times)
    differences = new_times - possible_times
    return all(x -> abs(x) < 200, differences)
end

const Triple = Tuple{Int64, Int64, Int64}
const SetOfLabels = Vector{Label}
const LabelTriples = Vector{TripleLabel}
# this function extends a triple of labels (states) in the backward direction to another point
# function extend_labels(label1::Label, label2::Label, label3::Label, label4::Label, label5::Label,  to_point::Int64)
function extend_labels(label1::Label, label2::Label, label3::Label,  to_point::Int64, cur_label_id::Int64, distance, scenarios)

    point = label3.point
    # first we should find the time of the extended label 
    # for this, we sort labels in the descending order of their time 
    prev_states = [label1, label2, label3]
    # visited_points = []
    visited_points = unique!(vcat(vcat(map(x -> x.visited_points, prev_states)...), [to_point]))
    sort!(prev_states, by = x -> x.time, rev = true)
    # we find the maximum time of the extended label
    # which is equal to min_i{label_i.time - scenarios[point, i].time}
    time = minimum([prev_states[i].time - distance[point, to_point] - scenarios[point, i].time for i=1:3])
    time < 0 && return nothing
    profit = sum([(prev_states[i].profit + scenarios[point, i].profit)*scenarios[point, i].prob for i=1:3])
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


#we now print the solution stored in the best label
function get_paths_dict(label::Label, scenarios)

    #if we have only one previous state, it necessarily corresponds to returning to the depot
    if length(label.prev_states) == 1
        return Dict([0]=>1.0)
    end

    prev_point = label.prev_states[1].point

    # we merge path dictionaries of three previous states
    # when merging, we sum the probabilities for the same paths
    paths_dict = Dict{Vector{Int64}, Float64}()
    for i in 1:3
        for (path, prob) in get_paths_dict(label.prev_states[i], scenarios)
            merge!(+, paths_dict, Dict(vcat(path,[prev_point])=>prob*scenarios[prev_point, i].prob))
        end
    end

    return paths_dict
end
end
