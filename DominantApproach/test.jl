a = [[rand(200:800) for i in 1:50]; [rand(0:100) for i in 1:50]]

a = [136, 125, 113, 100, 50]
sort!(a, rev=true )
N_SCENARIOS = 3
times = [i * 10 for i in 1:N_SCENARIOS]
ref_index = 4
@show a
function get_triples(labels, times, ref_index, N_SCENARIOS)
  # array to keep indices of chosen labels
  if N_SCENARIOS == 1
    return [labels[ref_index]]
  end

  indices = [ref_index]
  ref_time = labels[ref_index] - times[1]
  @show ref_time
  extensions = []

  # last_index = 1
  # while last_index < ref_index && (labels[last_index] - times[end]) > ref_time && (labels[last_index+1] - times[end]) <= ref_time
  #   last_index += 1
  #   # if new_index < 1
  #   #   return []
  #   # end
  # end
  # ref_time = min(ref_time, labels[last_index] - times[end])
  # @show last_index
  new_index = 1
  for i in 1:(N_SCENARIOS-1)
    # new_index = 1 #indices[end]
    # keep adding labels to extensions until reach the end of the array.
    # If we reached it and didn't gather enough labels, we return empty array.
    while new_index < ref_index && (labels[new_index] - times[end-i+1]) >= ref_time #&& (labels[new_index+1] - times[end-i+1]) <= ref_time
      println("enter")

      println(labels[new_index] - times[end-i+1])
      println(labels[new_index+1] - times[end-i+1])
      new_index += 1
      # if new_index < 1
      #   return []
      # end
    end
    @show new_index
    if i == 1
      ref_time = min(ref_time, labels[new_index] - times[end])
    end
    if new_index < ref_index && (labels[new_index] - times[end-i+1]) < ref_time
      new_index -=1
    end
    insert!(indices, 2, new_index)
  end
  @show ref_time
  current_times = [labels[i] for i in indices]
  current_times[1] = ref_time
  @show current_times
  # current_times = current_times .-= (labels[ref_index] - ref_time)
  # with variable denotes first index which do not fall into reference index
  start_index = 2

  # we iterate until meet non reference label or until all labels fall into reference
  # maybe we should add here checking that the result time should be nonnegative
  @show current_times
  @show indices
  while current_times[end] >= labels[ref_index] && (length(labels) == ref_index || current_times[1] >= labels[indices[1]+1])
    push!(extensions, [labels[i] for i in indices])

    for ind in indices[start_index:end]
      if ind >=ref_index
        start_index += 1
      end
    end
    if start_index > N_SCENARIOS
      break
    end
    @show start_index
    # calculating shifts for each label in extension to fall into next value
    shifts = [current_times[i] - labels[indices[i]+1] for i in start_index:N_SCENARIOS]
    indices_to_shift = []
    min = shifts[1]
    for (i, s) in enumerate(shifts)
      if s < min
        min = s
        indices_to_shift = [i+start_index-1]
      elseif s == min
        push!(indices_to_shift, i+start_index-1)
      end
    end
    for i in indices_to_shift
      indices[i] += 1
    end
    current_times  .-= min

  end
  return extensions
end

for extension in get_triples(a, times, ref_index, N_SCENARIOS)
  println(extension)
end




    # @show reverse(indices)
    # @show reverse(shifts)
    # println("NEW LABELS $([a[i] for i in reverse(indices)]) shift is $min shifted $indices_to_shift")
    # println("CURR TIMES $(reverse(current_times))")
    # println("CURR INDEX $(reverse(indices))")
    # println()
    # push!(extensions, [labels[i] for i in indices])

  # @show reverse(current_times)


  # third_shift = third_time - a[third_index+1]
  # second_shift = second_time - a[second_index + 1]
  # println()
  # # println("NEW TIMES [$third_time, $second_time, $new_time]")
  # @show third_shift
  # @show second_shift
  # if third_shift < second_shift
  #   global third_index += 1
  # elseif third_shift > second_shift
  #   global second_index += 1
  # else
  #   global third_index += 1
  #   global second_index += 1
  # end
  # global new_time -= min(second_shift, third_shift)
  # global second_time -= min(second_shift, third_shift)
  # global third_time -= min(second_shift, third_shift)
  # println("NEW TRIPLE [$(a[third_index]), $(a[second_index]), $(a[ref_index])], new time is $new_time ")
  # println("NEW TIMES [$third_time, $second_time, $new_time]")
  # println()
