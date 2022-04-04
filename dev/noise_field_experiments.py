import math
import numpy as np


def reset_seed():
    np.random.seed(7)


limit = 120
scale = 0.3

#lets make notes and try and figure out how this all works

# so this is literally just setting the "limit" to be a factor of 120
# and the "factor" to be a divisor of 120
limit = math.ceil(limit / 120) * 120
shape = (limit, limit)
factors = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60, 120]

# which then determines the "resolution" i.e. how matny cycles happen
res = factors[math.floor(scale * len(factors))]
res = (res, res)

# note quite sure what delta does yet
# its a tuple of the times res fits into shape
# and then d is the number of times the shape is divisible by res
delta = (res[0] / shape[0], res[1] / shape[1])
d = (shape[0] // res[0], shape[1] // res[1])
# creating mesh grid from that
grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1
# Gradients

# bunch of random angles for each resolution (makes sense)
reset_seed()
angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
# thne concatenating the sin and cos of those ganes
gradients = np.dstack((np.cos(angles), np.sin(angles)))
# don't really know why these have been binary labelled, it's confusing
# but basically, they're the gradients, repeating a bunch of times
gradient_1 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
gradient_2 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
gradient_3 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
gradient_4 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)
# Ramps, which look like they're using the mesh grid to calculate the 4 diffent gradients
ramp_1 = np.sum(grid * gradient_1, 2)
ramp_2 = np.sum(np.dstack((grid[:, :, 0]-1, grid[:, :, 1])) * gradient_2, 2)
ramp_3 = np.sum(np.dstack((grid[:, :, 0], grid[:, :, 1]-1)) * gradient_3, 2)
ramp_4 = np.sum(np.dstack((grid[:, :, 0]-1, grid[:, :, 1]-1)) * gradient_4, 2)
# Interpolation of "t" based on that
t = 6*grid**5 - 15*grid**4 + 10*grid**3
# combining the ramps together
combined_ramp_1 = ramp_1*(1-t[:, :, 0]) + t[:, :, 0]*ramp_2
combined_ramp_2 = ramp_3*(1-t[:, :, 0]) + t[:, :, 0]*ramp_4
# then brinding together into the final field
field = np.sqrt(2)*((1-t[:, :, 1])*combined_ramp_1
                    + t[:, :, 1]*combined_ramp_2)
field = (field + 1) / 2


# question is, how do we extend this field? Or just create a section of it?
# feels like really this comes from the mesh grid somehow
# delta is going to affect the number of size of the grid
# feels a lot like making a big grid, but then subsetting it before progressing would work nicely

def whole_grid(limit):

    # so this is literally just setting the "limit" to be a factor of 120
    # and the "factor" to be a divisor of 120
    limit = math.ceil(limit / 120) * 120
    shape = (limit, limit)
    factors = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60, 120]

    # which then determines the "resolution" i.e. how matny cycles happen
    res = factors[math.floor(scale * len(factors))]
    res = (res, res)

    # note quite sure what delta does yet
    # its a tuple of the times res fits into shape
    # and then d is the number of times the shape is divisible by res
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    # creating mesh grid from that
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]:delta[1]].transpose(1, 2, 0) % 1
    # Gradients
    reset_seed()
    # bunch of random angles for each resolution (makes sense)
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    # thne concatenating the sin and cos of those ganes
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    # don't really know why these have been binary labelled, it's confusing
    # but basically, they're the gradients, repeating a bunch of times
    gradient_1 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    gradient_2 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    gradient_3 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
    gradient_4 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)
    # Ramps, which look like they're using the mesh grid to calculate the 4 diffent gradients
    ramp_1 = np.sum(grid * gradient_1, 2)
    ramp_2 = np.sum(
        np.dstack((grid[:, :, 0]-1, grid[:, :, 1])) * gradient_2, 2)
    ramp_3 = np.sum(
        np.dstack((grid[:, :, 0], grid[:, :, 1]-1)) * gradient_3, 2)
    ramp_4 = np.sum(
        np.dstack((grid[:, :, 0]-1, grid[:, :, 1]-1)) * gradient_4, 2)
    # Interpolation of "t" based on that
    t = 6*grid**5 - 15*grid**4 + 10*grid**3
    # combining the ramps together
    combined_ramp_1 = ramp_1*(1-t[:, :, 0]) + t[:, :, 0]*ramp_2
    combined_ramp_2 = ramp_3*(1-t[:, :, 0]) + t[:, :, 0]*ramp_4
    # then brinding together into the final field
    field = np.sqrt(2)*((1-t[:, :, 1])*combined_ramp_1
                        + t[:, :, 1]*combined_ramp_2)
    field = (field + 1) / 2
    return field


def right_slice_grid(total_limit, start_point):
    # so this is literally just setting the "limit" to be a factor of 120
    # and the "factor" to be a divisor of 120
    limit = total_limit
    limit = math.ceil(limit / 120) * 120
    shape = (limit, limit)
    factors = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60, 120]

    # which then determines the "resolution" i.e. how matny cycles happen
    res = factors[math.floor(scale * len(factors))]
    res = (res, res)

    # note quite sure what delta does yet
    # its a tuple of the times res fits into shape
    # and then d is the number of times the shape is divisible by res
    delta = (res[0] / shape[0], res[1] / shape[1])
    d = (shape[0] // res[0], shape[1] // res[1])
    # creating mesh grid from that
    grid = np.mgrid[0:res[0]:delta[0], 0:res[1]                    :delta[1]].transpose(1, 2, 0) % 1

    # lets slice the grid for the right side
    grid = grid[start_point:, ]

    # Gradients
    reset_seed()
    # bunch of random angles for each resolution (makes sense)
    angles = 2*np.pi*np.random.rand(res[0]+1, res[1]+1)
    # thne concatenating the sin and cos of those ganes
    gradients = np.dstack((np.cos(angles), np.sin(angles)))
    # don't really know why these have been binary labelled, it's confusing
    # but basically, they're the gradients, repeating a bunch of times
    gradient_1 = gradients[0:-1, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    gradient_2 = gradients[1:, 0:-1].repeat(d[0], 0).repeat(d[1], 1)
    gradient_3 = gradients[0:-1, 1:].repeat(d[0], 0).repeat(d[1], 1)
    gradient_4 = gradients[1:, 1:].repeat(d[0], 0).repeat(d[1], 1)e
    # Ramps, which look like they're using the mesh grid to calculate the 4 diffent gradients
    ramp_1 = np.sum(grid * gradient_1, 2)
    ramp_2 = np.sum(
        np.dstack((grid[:, :, 0]-1, grid[:, :, 1])) * gradient_2, 2)
    ramp_3 = np.sum(
        np.dstack((grid[:, :, 0], grid[:, :, 1]-1)) * gradient_3, 2)
    ramp_4 = np.sum(
        np.dstack((grid[:, :, 0]-1, grid[:, :, 1]-1)) * gradient_4, 2)
    # Interpolation of "t" based on that
    t = 6*grid**5 - 15*grid**4 + 10*grid**3
    # combining the ramps together
    combined_ramp_1 = ramp_1*(1-t[:, :, 0]) + t[:, :, 0]*ramp_2
    combined_ramp_2 = ramp_3*(1-t[:, :, 0]) + t[:, :, 0]*ramp_4
    # then brinding together into the final field
    field = np.sqrt(2)*((1-t[:, :, 1])*combined_ramp_1
                        + t[:, :, 1]*combined_ramp_2)
    field = (field + 1) / 2
    return field
