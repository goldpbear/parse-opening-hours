from opening_hours.models.day import Day, DaysEnum
import logging, os

logger = logging.getLogger(__name__)

class Days():
	"""
	This class represents a set of days and provides
	some helpful methods to interperet these sets from shortcuts (like
	"weekdays"), iterate over the days, etc.


	"""
	days = set({})
	#TODO: support days with exceptions (like "Monday to friday but not thurdsays")
	@classmethod
	def from_shortcut_string(cls, days_string, assume_type=None):
		"""
		create a time object from a string
		"""
		logger.debug("creating days object from shortcut: " + days_string)
		if days_string is None:
			raise TypeError("Cannot create Days Object from value None")
			
		day = days_string.lower()

		# set up some shortcut ranges
		allweek = cls(DaysEnum.MONDAY, DaysEnum.SUNDAY)
		workweek = cls(DaysEnum.MONDAY, DaysEnum.FRIDAY)

		if "weekday" in day:
			return workweek
		elif "business" in day:
			return workweek
		elif "work" in day:
			return workweek
		elif "5" in day:
			return workweek
		elif "7" in day:
			return allweek
		elif "all" in day and "week" in day:
			return allweek
		elif "every" in day:
			return allweek
		elif "daily" in day:
			return allweek
		elif "weekend" in day:
			return cls(DaysEnum.SATURDAY, DaysEnum.SUNDAY)
		elif day == "":
			# if no day is specified, assume the intention is all week
			return allweek

		raise ValueError("string '" + days_string + "' does not match a known pattern")
			
	@classmethod
	def from_parse_results(cls, result):
		days = None

		if "startday" in result:
			logger.info("range date detected")
			# this is a date range that includes the intervening days
			start_day = Day.from_string(result.get("startday")[0])
			end_day = result.get("endday")[0]
			logger.debug(end_day)
			end_day = Day.from_string(end_day) if end_day is not None else end_day
			days = cls(start_day, end_day)
		
		if "day" in result:
			logger.info("list date detected")

			for day in result.get("day"):
				if days:
					days.add(Day.from_string(day).as_enum())
				else:
					days = Days(Day.from_string(day), Day.from_string(day))
		
		if "day_shortcuts" in result:
			logger.info("shortcut date detected")
			shortcut_days = cls.from_shortcut_string(result.get( "day_shortcuts")[0])
			for day in shortcut_days:
				if days:
					days.add(day)
				else:
					days = Days(day, day)
				

		if days is None:
			logger.info("unspecified date detected ")
			# logger.debug(vars(result))
			# nothing specified, assumeit means every day
			return cls(DaysEnum.MONDAY, DaysEnum.SUNDAY)
		return days
		
	def __init__(self, start_day, end_day):
		if start_day is None or end_day is None:
			raise TypeError("Cannot create Days Object from value None")
	
		logger.debug("creating days from " + str(start_day) + " and " + str(end_day))

		self.days = set(self._expand_day_range(start_day, end_day))
		
	def __str__(self):
		daystrings = [str(Day(d)) for d in self.days]
		return "Days<" + ''.join(daystrings) + ">"

	def _expand_day_range(self, start_day, end_day):
		# if end_day is None:
		# 	return [start_day]
		week = list(DaysEnum)
		start_index = week.index(start_day)
		end_index = week.index(end_day)

		if end_index < start_index:
			# if the end day is sooner in the week than the start
			end_index += start_index

		days = set({})
		for x in range(start_index, end_index+1):
			#ensure the indices wrap around to the beginning of the week
			day_index = x % 7
			days.add(week[day_index])
	
		return set(days)

	def add(self, day):
		if isinstance(day, DaysEnum):
			self.days.add(day)
		elif isinstance(day, Day):
			self.days.add(day.as_enum())
		else:
			# don't attempt to add unrelated types
			raise NotImplementedError()

	def __iter__(self):
		return iter(self.sort())

	def sort(self):
		days = [Day(d) for d in self.days]
		return sorted(days)
	
	def __eq__(self, other):
		if not isinstance(other, Days):
			# don't attempt to compare against unrelated types
			raise NotImplementedError()
		return self.days == other.days

