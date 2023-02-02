import pygame
import random
import math

class Paddle:
	def __init__(self, x, y, v_y, width=20, height=100, color=(255,255,255)):
		# Set how fast the paddle moves
		self.v_y = v_y
		# Set the paddle's color
		self.color = color

		# Set up the image to display on the screen
		self.surface = pygame.Surface((width, height))
		self.surface.fill(color)
		self.surface = self.surface.convert()

		# Get the rectangle that is that surface
		self.rect = self.surface.get_rect()

		# Set the position of that rectangle
		self.rect.x = x
		self.rect.y = y - self.rect.height/2

	def update(self, rate, bounds, dirMove = 0):
		# Update the position
		self.rect.y += self.v_y*rate*dirMove

		# Don't let the paddle move too far
		if self.rect.y < 0:
			self.rect.y = 0
		elif self.rect.y > bounds[1] - self.rect.height:
			self.rect.y = bounds[1] - self.rect.height

	def draw(self, screen):
		# Display on the screen
		screen.blit(self.surface, self.rect)


class Ball:
	def __init__(self, x, y, v_x, v_y, r, color=(255, 255, 255)):
		# The ball's velocities
		self.v_x = v_x
		self.v_y = v_y

		# The ball's color
		self.color = color

		# Set up the circle to display on the screen
		self.surface = pygame.Surface((2*r, 2*r))
		pygame.draw.circle(self.surface, color, (r, r), r)
		self.surface = self.surface.convert_alpha()

		# Get the containing rectangle
		self.rect = self.surface.get_rect()

		# Set up the ball's position
		self.rect.x = x - r
		self.rect.y = y - r

	def update(self, rate, bounds, leftPaddle, rightPaddle):
		# Move the ball
		self.rect.x += self.v_x*rate
		self.rect.y += self.v_y*rate

		# If it goes offscreen, someone won!
		if self.rect.x < 0:
			return 'left'
		elif self.rect.x > bounds[0] - self.rect.width:
			return 'right'

		# If it hits the top or bottom, bounce
		if self.rect.y < 0:
			self.rect.y = 0
			self.v_y *= -1
		elif self.rect.y > bounds[1] - self.rect.height:
			self.rect.y = bounds[1] - self.rect.height
			self.v_y *= -1

		# If it hits a paddle, bounce
		if self.rect.colliderect(leftPaddle.rect):
			self.v_x *= -1
			self.v_x *= 1.1
			return 'left paddle'
		elif self.rect.colliderect(rightPaddle.rect):
			self.v_x *= -1
			self.v_x *= 1.1
			return 'right paddle'

		return False

	def draw(self, screen):
		# Display on the screen
		screen.blit(self.surface, self.rect)


class Pong:
	# This is a helper method to reset the locations of the paddles and ball
	def initObjects(self, size, ballSpeed, playerSpeed, cpuSpeed):
		# The size of the screen
		width, height = size

		# Set the ball going at a random angle
		angle = random.choice((1, -1))*(random.uniform(0, 5*math.pi/8) + 5*math.pi/16)
		self.ball = Ball(width/2, height/2, ballSpeed*math.sin(angle), ballSpeed*math.cos(angle), 20, color=(0, 0, 255))

		# Set up the paddles
		self.player1Paddle = Paddle(10, height/2, playerSpeed, color=(255, 0, 0))
		self.cpuPaddle = Paddle(width - 30, height/2, cpuSpeed, color=(0, 255, 0))

	def __init__(self, size=(1920//2, 1080//2)):
		# How big the screen should be
		self.size = size

		# Set up for displaying text
		self.myfont = pygame.font.SysFont(None, 30)

		# Set up the background of the game
		self.screen = pygame.display.set_mode(size)
		self.background = pygame.Surface(self.screen.get_size())
		self.background.fill((0, 0, 0))
		self.background = self.background.convert()

		# Set up a clock to limit the FPS
		self.clock = pygame.time.Clock()

		# Set the maximum FPS
		self.FPS = 30.0

		# How long has the user played the game?
		self.playtime = 0.0

		# How many wins does each side have?
		self.lwins = 0
		self.rwins = 0

		# Pause the game at the beginning for three seconds
		self.paused = self.FPS*3

		# Call the helper method
		self.initObjects(size, 0.4, 0.5, 0.5)

		# How many milliseconds since the previous frame
		self.milliseconds = 0


	def inputMove(self):
		# Which keys have been pressed?
		keys_pressed = pygame.key.get_pressed()

		if keys_pressed[pygame.K_DOWN]: # If down is pressed, move down
			self.player1Paddle.update(self.milliseconds, self.screen.get_size(), 1)
		elif keys_pressed[pygame.K_UP]: # If up is pressed, move up
			self.player1Paddle.update(self.milliseconds, self.screen.get_size(), -1)


		# If the ball is above the CPU, move up, otherwise move down
		if self.ball.rect.y + self.ball.rect.height < self.cpuPaddle.rect.y:
			self.cpuPaddle.update(self.milliseconds, self.screen.get_size(), -1)
		elif self.ball.rect.y > self.cpuPaddle.rect.y + self.cpuPaddle.rect.height:
			self.cpuPaddle.update(self.milliseconds, self.screen.get_size(), 1)


		doQuit = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT: # If we exit, leave
				doQuit = True
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE: # If we press escape, leave
					doQuit = True
				elif event.key == pygame.K_SPACE: # If we press space, reset the game
					self.__init__() # This reinitializes everything

		return doQuit

	def update(self):
		# Get how long it has been since the last frame
		self.milliseconds = self.clock.tick(self.FPS)
		# Update how long we've been playing
		self.playtime += self.milliseconds/1000.0

		# If we aren't paused
		if self.paused == 0:
			# Check if the ball hit anything
			hitSide = self.ball.update(self.milliseconds, self.screen.get_size(), self.player1Paddle, self.cpuPaddle)

			# If it hit a side, update who won and reset
			if hitSide == 'left' or hitSide == 'right':
				if hitSide == 'right':
					self.lwins += 1
				elif hitSide == 'left':
					self.rwins += 1
				self.initObjects(self.size, 0.4, 0.5, 0.5)
		else:
			# Reduce the pause timer
			self.paused -= 1


	def draw(self):
		# Display the background
		self.screen.blit(self.background, (0, 0))

		# Display the FPS and playtime on the header for the game
		text = "FPS: {0:.2f}   Playtime: {1:.2f}".format(self.clock.get_fps(), self.playtime)
		pygame.display.set_caption(text)

		# Display the score
		scoreTitle = self.myfont.render(' SCORE ', True, (255, 255, 255))
		self.screen.blit(scoreTitle, (self.screen.get_width()/2 - scoreTitle.get_width()/2, 20))
		score = self.myfont.render('{0}  {1}'.format(self.lwins, self.rwins), True, (255, 255, 255))
		self.screen.blit(score, (self.screen.get_width()/2 - score.get_width()/2, 20 + scoreTitle.get_height()))

		# Draw the paddles and ball
		self.ball.draw(self.screen)
		self.player1Paddle.draw(self.screen)
		self.cpuPaddle.draw(self.screen)

		# If the game is paused, display the timer
		if self.paused != 0:
			countdownFont = pygame.font.SysFont(None, int(1.5*min(self.screen.get_size())*(((self.paused-1)%self.FPS)+1)/self.FPS))
			countdown = countdownFont.render('{}'.format(math.ceil(self.paused/self.FPS)), True, (255, 255, 255))
			self.screen.blit(countdown, (self.screen.get_width()/2 - countdown.get_width()/2, self.screen.get_height()/2 - countdown.get_height()/2))

		# Push everything to the screen
		pygame.display.flip()

if __name__ == '__main__':
	pygame.init()

	pong = Pong()

	doQuit = False
	while not doQuit:

		doQuit = pong.inputMove()

		pong.update()

		pong.draw()

	pygame.quit()
