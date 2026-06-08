module DispatchModel

using JuMP
import HiGHS

export Generator, merit_order_dispatch, total_cost

struct Generator
    name::String
    marginal_cost::Float64
    capacity::Float64

    function Generator(name::AbstractString, marginal_cost::Real, capacity::Real)
        marginal_cost < 0 && throw(ArgumentError("marginal_cost must be non-negative"))
        capacity < 0 && throw(ArgumentError("capacity must be non-negative"))
        new(String(name), Float64(marginal_cost), Float64(capacity))
    end
end

function merit_order_dispatch(demand::Real, generators)
    demand < 0 && throw(ArgumentError("demand must be non-negative"))

    demand_value = Float64(demand)
    items = collect(generators)

    if isempty(items)
        demand_value <= 1e-9 && return Pair{String, Float64}[]
        throw(ArgumentError("demand exceeds available capacity"))
    end

    names = [generator.name for generator in items]
    length(unique(names)) == length(names) ||
        throw(ArgumentError("generator names must be unique"))

    model = Model(HiGHS.Optimizer)
    set_silent(model)

    @variable(model, 0 <= output[i in eachindex(items)] <= items[i].capacity)
    @constraint(model, sum(output[i] for i in eachindex(items)) == demand_value)
    @objective(
        model,
        Min,
        sum(items[i].marginal_cost * output[i] for i in eachindex(items))
    )

    optimize!(model)

    status = termination_status(model)
    if status == JuMP.MOI.INFEASIBLE
        throw(ArgumentError("demand exceeds available capacity"))
    elseif status != JuMP.MOI.OPTIMAL
        throw(ErrorException("dispatch optimisation failed with status $status"))
    end

    dispatch = Pair{String, Float64}[]

    for (i, generator) in pairs(items)
        generation = value(output[i])
        if generation > 1e-7
            push!(dispatch, generator.name => generation)
        end
    end

    return dispatch
end

function total_cost(dispatch, generators)
    costs = Dict(generator.name => generator.marginal_cost for generator in generators)
    return sum(costs[item.first] * item.second for item in dispatch)
end

end

if abspath(PROGRAM_FILE) == @__FILE__
    using .DispatchModel

    generators = [
        Generator("wind", 0.0, 35.0),
        Generator("solar", 3.0, 25.0),
        Generator("gas", 75.0, 60.0),
    ]

    dispatch = merit_order_dispatch(80.0, generators)
    println("Dispatch: ", dispatch)
    println("Total cost: ", round(total_cost(dispatch, generators); digits = 2))
end
