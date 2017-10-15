import random

class Markov(object):
	def __init__(self, array, chain):
		self.cache = {}
		self.chain_length = chain
		for trigger in array:
			self.database(trigger.encode('ascii', 'ignore').split())

	def chain(self,trigger):               
		if len(trigger) < self.chain_length:
			return

		for i in range(len(trigger)+1 - self.chain_length):
			yield trigger[i:i+self.chain_length]
					
	def database(self,trigger):
		for link in self.chain(trigger):
			key = tuple([x.lower().translate(None, '(")') for x in link[:-1]])
			if key in self.cache:
				self.cache[key].append(link[-1].translate(None, '()'))
			else:
				self.cache[key] = [link[-1].translate(None, '()')]
							
	def generate_markov_text(self, size=25):
		seed_words = random.choice(self.cache.keys())
		gen_words = []
		
		for i in xrange(size):
			if seed_words not in self.cache:
				seed_words = random.choice(self.cache.keys())
			chain_word = random.choice(self.cache[seed_words])
			if (gen_words and gen_words[-1][-1] in ['.','!','?'] and gen_words[-1][-3:-1]!='...'):
				gen_words.append(chain_word.capitalize())
			else:
				gen_words.append(chain_word.lower())
			seed_words = seed_words[1:] + (chain_word,)
		
		
		
		
		return ' '.join(gen_words)