import pygame
import numpy as np

from snake_app import Grid, Snake


def get_adjusted_centre_coordinates(pos, grid, dir):
    coords = grid.get_coordinates(pos)
    match(dir):
        case (0,-1):
            return((int(coords[0] + 0.5*grid.block_width), coords[1]))
        case (1,-1):
            return((int(coords[0] + grid.block_width), coords[1]))
        case (1,0):
            return((int(coords[0] + grid.block_width), int(coords[1] + 0.5*grid.block_width)))
        case (1,1):
            return((int(coords[0] + grid.block_width), int(coords[1] + grid.block_width)))
        case (0,1):
            return((int(coords[0] + 0.5*grid.block_width), int(coords[1] + grid.block_width)))
        case (-1,1):
            return((coords[0], int(coords[1] + grid.block_width)))
        case (-1,0):
            return((coords[0], int(coords[1] + 0.5*grid.block_width)))
        case (-1,-1):
            return(coords)


def get_centre_coordinates(pos, grid):
    coords = grid.get_coordinates(pos)
    return((int(coords[0] + 0.5*grid.block_width), int(coords[1] + 0.5*grid.block_width)))


def arrow_to_move(direction, key, move):
    """Convert pressed arrow key to direction the snake needs to turn in.
    
    Can only stay moving forward or turn left or turn right.
    """

    if key == pygame.K_UP:
        match(direction):
            case (-1,0):
                move = 'right'
            case (1,0):
                move = 'left'
    elif key == pygame.K_DOWN:
        match(direction):
            case (1,0):
                move = 'right'
            case (-1,0):
                move = 'left'
    elif key == pygame.K_RIGHT:
        match(direction):
            case (0,-1):
                move = 'right'
            case (0,1):
                move = 'left'
    elif key == pygame.K_LEFT:
        match(direction):
            case (0,1):
                move = 'right'
            case (0,-1):
                move = 'left'

    return move


def main(settings):
    
    #initialize the grid the game will be modelled from
    grid = Grid(settings['grid_size'], settings['block_width'], settings['grid_width'])

    #pygame setup
    screen = pygame.display.set_mode(grid.board_size)
    clock = pygame.time.Clock()
    running = True
    dt = 0

    #initialize the snake
    snake = Snake(settings['grid_size'], settings['length'])
    snake.look()

    #choose what line type
    line_types = ['none', 'walls', 'food', 'body']
    line_type = line_types[0]

    while running:

        #stops from pressing twice in one frame and then moving in forbidden directions
        key_pressed = False
        move = 'forward'

        for event in pygame.event.get():
            #so can quit
            if event.type == pygame.QUIT: 
                running = False
                break
            
            #change direction (in allowed directions)
            if event.type == pygame.KEYDOWN:
                if key_pressed == False:
                    key_pressed = True
                    move = arrow_to_move(snake.direction, event.key, move)
                    if event.key == pygame.K_SPACE:
                        line_types.append(line_types[0])
                        del line_types[0]
                        line_type = line_types[0]
            
        #move in the chosen direction
        snake.move(move)

        #check if we've died
        if snake.dead:
            running = False
            break

        #look now so we can draw lines
        snake.look()


        #fill the screen to wipe last frame
        screen.fill((40,40,40))

        #visualize the snake and food on the screen
        pygame.draw.rect(screen, 'red', pygame.Rect(grid.get_coordinates(snake.target.position), (grid.block_width, grid.block_width)))
        for pos in snake.body:
            pygame.draw.rect(screen, 'green', pygame.Rect(grid.get_coordinates(pos), (grid.block_width, grid.block_width)))

        #choose what lines to draw
        direction = snake.direction
        direction_right = (direction[0] - direction[1], direction[0] + direction[1])
        start = get_centre_coordinates(snake.body[0], grid)
        match(line_type):
            case 'walls':
                #draw lines from center of head to walls
                for d, distance in vars(snake.vision.walls).items():
                    match(d):
                        case 'f' | 'r' | 'b' | 'l':
                            end = get_adjusted_centre_coordinates(tuple(np.add(np.array(snake.body[0]), np.multiply(np.array(direction), distance - 1))), grid, direction)
                            direction = (-direction[1], direction[0])
                        case 'fr' | 'br' | 'bl' | 'fl':
                            end = get_adjusted_centre_coordinates(tuple(np.add(np.array(snake.body[0]), np.multiply(np.array(direction_right), distance - 1))), grid, direction_right)
                            direction_right = (-direction_right[1], direction_right[0])
                    pygame.draw.aaline(screen, 'purple', start, end)

            case 'food':
                #draw food search lines
                for d, distance in vars(snake.vision.food).items():
                    match(d):
                        case 'f' | 'r' | 'b' | 'l':
                            end = get_adjusted_centre_coordinates(tuple(np.add(np.array(snake.body[0]), np.multiply(np.array(direction), min(distance - 1, getattr(snake.vision.walls, d) - 1)))), grid, direction)
                            direction = (-direction[1], direction[0])
                        case 'fr' | 'br' | 'bl' | 'fl':
                            end = get_adjusted_centre_coordinates(tuple(np.add(np.array(snake.body[0]), np.multiply(np.array(direction_right), min(distance - 1, getattr(snake.vision.walls, d) - 1)))), grid, direction_right)
                            direction_right = (-direction_right[1], direction_right[0])
                    pygame.draw.aaline(screen, 'yellow', start, end)

            case 'body':
                #draw lines from head to body
                for d, distance in vars(snake.vision.body).items():
                    match(d):
                        case 'f' | 'r' | 'b' | 'l':
                            end = get_adjusted_centre_coordinates(tuple(np.add(np.array(snake.body[0]), np.multiply(np.array(direction), min(distance - 1, getattr(snake.vision.walls, d) - 1)))), grid, direction)
                            direction = (-direction[1], direction[0])
                        case 'fr' | 'br' | 'bl' | 'fl':
                            end = get_adjusted_centre_coordinates(tuple(np.add(np.array(snake.body[0]), np.multiply(np.array(direction_right), min(distance - 1, getattr(snake.vision.walls, d) - 1)))), grid, direction_right)
                            direction_right = (-direction_right[1], direction_right[0])
                    pygame.draw.aaline(screen, 'blue', start, end)

        #display the changes
        pygame.display.flip()

        #limit the fps in such a way that it takes 5s to cross the board horizontally
        dt = clock.tick(grid.size[0]/5) / 1000

    pygame.quit()


if __name__ == '__main__':
    from settings import settings
    main(settings)
