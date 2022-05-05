class Alphabet:
	def __init__(self):
		self.ru_alphabet = {
			"a":"а",
			"b":"б",
			"c":"к",
			"d":"д",
			"e":"е",
			"f":"ф",
			"g":"г",
			"h":"х",
			"i":"и",
			"j":"ж",
			"k":"к",
			"l":"л",
			"m":"м",
			"n":"н",
			"o":"о",
			"p":"п",
			"q":"к",
			"r":"р",
			"s":"с",
			"t":"т",
			"u":"у",
			"v":"в",
			"w":"в",
			"x":"х",
			"y":"ю",
			"z":"з",
			"yu":"ю",
			"ch":"ч",
			"zh":"ж",
			"sh":"ш",
			"shch":"щ",
			"ye":"е",
			"ts":"ц",
			"ya":"я",
			"ju":"я",
			" ":" ",
		}

	def go_translit(self, text:str) -> str:
		translit_text = ""
		print(text, "--!_!_!_")
		for letter in text:
			if letter in self.ru_alphabet:
				translit_text += self.ru_alphabet[letter]
			else:
				translit_text += letter

		print(translit_text, "---")
		return translit_text