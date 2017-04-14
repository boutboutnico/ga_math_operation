
import sys
import math
import random
from bitstring import BitArray

table = {
 '0000' : 0,
 '0001' : 1,
 '0010' : 2,
 '0011' : 3,
 '0100' : 4,
 '0101' : 5,
 '0110' : 6,
 '0111' : 7,
 '1000' : 8,
 '1001' : 9,
 '1010' : '+',
 '1011' : '-',
 '1100' : '*',
 '1101' : '/',
 '1110' : '#',
 '1111' : '#',
 }

FITNESS_MAX = 100.0
CROSSOVER_RATE = 0.7
MUTATION_RATE = 0.001

###	To Do ###
# Add multiple cut to crossover function
# Add GUI
# Add unittest
 
class Chromosome:
	'''Represents a chromosome
	 0110 1010 0101 1100 0100 1101 0010 1010 0001
	 6     +     5    *    4    /    2    +    1
	'''
	
	LENGTH = 4*11
	
	id = 0
	genes = BitArray()
	math_result = 0
	fitness = 0
	generation = 1
	
	def __init__(self):
		self.id = Chromosome.id
		Chromosome.id += 1
		val = random.randint(0, pow(2,(self.LENGTH)) - 1)
		self.genes = BitArray(uint=val, length=self.LENGTH)
		#~ print val, self.genes.bin
		
	def __str__(self):
		#~ result = str(id) + " "
		result = "[{:>3}:{:>3}] ".format(self.id, self.generation) 
		#~ result += "{} ".format(self.genes.bin)
		for i in xrange(0, self.LENGTH, 4):
			sub_genes = self.genes[i:i+4].bin
			if sub_genes in table:
				val = table[sub_genes]
				result += str(val) +  " "
		result += " = {:>3} ".format(self.math_result)
		result += "f:{:6.2f} ".format(self.fitness)
		return result


def main(argv):
	print "Genetic Algorithm"
	
	result_expected = int(argv[1])
	population_size = int(argv[2])
	generation_max = int(argv[3])
	print "Population size: {}".format(population_size)

	population = []
	generation_count = 1;
	cpt = 0

	# Generate initial population
	for i in xrange(0, population_size):
		population.append(Chromosome())
				

	while (cpt < generation_max):
		
		cpt += 1
		
		# Selection
		print "\n##########"
		print "Population: {}".format(population_size)
		print "Expected result: {}".format(result_expected)
		print "# Selection gen:{}/{}".format(generation_count, generation_max)
		selection(result_expected, population)
		
		the_best = get_the_best(population)
		print "\nBest: {}".format(the_best)
		print "Average: {:6.2f}".format(average(population))
		
		if (the_best.fitness >= FITNESS_MAX):
			break
		
		# Crossover
		print "# Crossover"
		
		total_fitness = get_total_fitness(population)
		#~ print "total fitness: {:6.2f}".format(total_fitness)
		
		generation_count += 1
		population = crossover(population, generation_count, total_fitness)
		
		# Mutation
		print "# Mutation"
		mutation(population)
		
		#~ tmp = raw_input("Press Enter to execute next step")
		
			
def mutation(population):
	
	for c in population:
		for i in xrange(0, Chromosome.LENGTH):
			if random.random() <= MUTATION_RATE:
				#~ print "mutation: " + str(i)
				#~ print c.genes, c.genes.bin
				c.genes.set(not c.genes[i], i)
				#~ print c.genes, c.genes.bin
	
	
def crossover(population, generation_count, total_fitness):
	
	new_population = []
	parents= []
	pick_count = len(population)/10	
	
	while (len(new_population) <= len(population)):
		
		if not parents:
			parents = roulette(population, total_fitness, pick_count)

		parent1 = parents[0]
		parent2 = parents[1]
		del parents[0:2]
	
		if random.random() <= CROSSOVER_RATE:
			cut = random.randint(0, Chromosome.LENGTH)
			
			child1 = Chromosome()
			child1.genes = parent1.genes[:cut] + parent2.genes[cut:]
			child1.generation = generation_count
			
			child2 = Chromosome()
			child2.genes = parent2.genes[:cut] + parent1.genes[cut:]
			child2.generation = generation_count
			
			new_population.append(child1)
			new_population.append(child2)
		else:
			if all(c.id != parent1.id for c in new_population):
				new_population.append(parent1)
			
			if all(c.id != parent2.id for c in new_population):
				new_population.append(parent2)
	
	return new_population
	
	
def roulette(population, total_fitness, pick_count):
	
	cuts = []
	parents = []
	
	# pick_count >= 2 and even
	if pick_count < 2: pick_count = 2
	if pick_count % 2 != 0: pick_count += 1
	
	# Generated random number between 0 and total_fitness
	for i in xrange(0, pick_count):
		cuts.append(random.randint(0, math.floor(total_fitness)))
	
	cumul_fitness = 0
	for chromo in population:
		cumul_fitness += chromo.fitness
		
		for c in cuts:
			if cumul_fitness >= c:
				parents.append(chromo)
		
		# Removed used cuts
		cuts = [c for c in cuts if not cumul_fitness >= c]

	return parents

	
def get_total_fitness(population):
	return sum(c.fitness for c in population)


# median, esperance, ecart-type, variance
def average(population):
	return sum(c.fitness for c in population) / len(population)


def get_the_best(population):
	
	best_fitness = max(c.fitness for c in population)
	
	for c in population:
		if c.fitness == best_fitness:
			return c
	print "error: get_the_best {}".format(best_fitness)
		

def selection(result_expected, population):
	for p in population:
		evaluate(p)
		fitness(result_expected, p)
		#~ print p


def fitness(result_expected, chromosome):
	if chromosome.math_result == result_expected:
		chromosome.fitness = FITNESS_MAX
	else:
		chromosome.fitness = (FITNESS_MAX - 1.0) \
		/(abs(result_expected - chromosome.math_result))


def evaluate(chromosome):
	result = 0
	operator = 0
	num_not_op = True	# First we want a number
	
	for i in xrange(0, Chromosome.LENGTH, 4):
	
		val = chromosome.genes[i:i+4].uint
		
		if num_not_op and is_digit(val):
			num_not_op = False
			
			if operator == 0:
				result += val
			elif operator == 1:
				result -= val
			elif operator == 2:
				result *= val
			elif operator == 3 and val != 0:
					result /= val
			
		elif not num_not_op and is_operator(val):
			num_not_op = True
			operator = val - 10
			
		else:
			break
			
	chromosome.math_result = result
			

def is_operator(genes):
	''' 1010 (10) <= genes <= 1101(13)'''
	return (10 <= genes and genes <= 13)


def is_digit(genes):
	'''0 <= digit <= 9'''	
	return (0 <= genes and genes <= 9)


if __name__=="__main__":
	main(sys.argv)
	
			


