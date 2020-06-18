#!/usr/bin/env python
# coding: utf-8

# ## Terraforming Mars Cost-Benefit Analysis
# <br>
# Terraforming Mars is a competitive board game developed by Jacob Fryxelius and published by FryxGames in 2016. Players take on the role of corporations tasked with making Mars habitable through the raising of the oxygen level, temperature, and ocean coverage, as well as sundry other projects to progress humanity.
# 
# Currently sitting at #4 on BoardGameGeek's ranked board game list, Terraforming Mars has found broad popularity among strategy board gamers in large part due to its variety and complexity. With 208 unique cards and 12 distinct corporations, players are put into an endless assortment of scenarios. This incredible depth means that players must often intuit their next move rather than deduce it from values and probabilities.
# 
# In a bid to add more deduction back into the equation, this analysis aims to take every card in Terraforming Mars and boil it down to a single value in credits (the game's main resource) for simple value-comparison.
# 
# Let's get started.

import numpy as np
from statistics import median
import pandas as pd
import seaborn as sns
import csv
import ast
import re

np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)

# The base_cards database, populated from a hand-entered csv, follows a couple of conventions:
# * When a resource is written in uppercase it refers to that resource's production, whereas when written in lowercase it refers to the resource iself.
# * All nouns are written in the singular in order to simplify pandas referencing.
# 
# The all_games database is a collection of stats from over 12,000 individually logged games downloaded from Simeon Simeonov's excellent [Terraforming Mars website](https://ssimeonoff.github.io/). The base_games database contains only the matches from all_games which were played with the full base version of the game.

# create databases
base_cards = pd.read_csv('TM_base_project_list.csv')
all_games = pd.read_csv('games_list.csv')
base_games = all_games[(all_games.expansions == "['CORPORATE']") & (all_games.map == "THARSIS")]

# First, an average number of generations for each player count must be derived from base_games. These will be used to determine the income which will be generated over the remainder of the game for a given card after the generation during which it is played. They'll also be used to split the game into four quarters to illustrate how a card's value changes over time.

# determine generation averages per player count
lastgen2p = int(round(base_games[base_games.players == 2].generations.mean()))
lastgen3p = int(round(base_games[base_games.players == 3].generations.mean()))
lastgen4p = int(round(base_games[base_games.players == 4].generations.mean()))
lastgen5p = int(round(base_games[base_games.players == 5].generations.mean()))

lastgens = {
            'lastgen2p': int(round(base_games[base_games.players == 2].generations.mean())),
            'lastgen3p': int(round(base_games[base_games.players == 3].generations.mean())),
            'lastgen4p': int(round(base_games[base_games.players == 4].generations.mean())),
            'lastgen5p': int(round(base_games[base_games.players == 5].generations.mean()))
           }

# average game length split into quarters with the median generation taken from each quarter
# X players, quarter N, median generation
gen_quarters = {
               '2pq1gen':round(lastgen2p/4/2),
               '2pq2gen':round(lastgen2p/4/2 + lastgen2p/4),
               '2pq3gen':round(lastgen2p/4/2 + lastgen2p/4*2),
               '2pq4gen':round(lastgen2p/4/2 + lastgen2p/4*3),
               '3pq1gen':round(lastgen3p/4/2),
               '3pq2gen':round(lastgen3p/4/2 + lastgen3p/4),
               '3pq3gen':round(lastgen3p/4/2 + lastgen3p/4*2),
               '3pq4gen':round(lastgen3p/4/2 + lastgen3p/4*3),
               '4pq1gen':round(lastgen4p/4/2),
               '4pq2gen':round(lastgen4p/4/2 + lastgen4p/4),
               '4pq3gen':round(lastgen4p/4/2 + lastgen4p/4*2),
               '4pq4gen':round(lastgen4p/4/2 + lastgen4p/4*3),
               '5pq1gen':round(lastgen5p/4/2),
               '5pq2gen':round(lastgen5p/4/2 + lastgen5p/4),
               '5pq3gen':round(lastgen5p/4/2 + lastgen5p/4*2),
               '5pq4gen':round(lastgen5p/4/2 + lastgen5p/4*3)
              }
keys2pgen = ['2pq1gen', '2pq2gen', '2pq3gen', '2pq4gen']
keys3pgen = ['3pq1gen', '3pq2gen', '3pq3gen', '3pq4gen']
keys4pgen = ['4pq1gen', '4pq2gen', '4pq3gen', '4pq4gen']
keys5pgen = ['5pq1gen', '5pq2gen', '5pq3gen', '5pq4gen']

# Next, each resource in the game must be converted to a number of credits. The [standard projects](https://3.bp.blogspot.com/-fs7vQZGRFs4/XAjAYOSBspI/AAAAAAAAFSA/kInbyuaLoLc0PANwJeFDpJditT5Ims3_wCLcBGAs/s1600/terraforming-mars-standard-projects-1.jpg) are set as listed on the game board, and steel and titanium as listed on the [player boards](https://cf.geekdo-images.com/medium/img/qa7YwBE6pc-ZR0relFRrzUAlQXw=/fit-in/500x500/filters:no_upscale()/pic2891980.jpg).  
# 
# Plants and heat are set by dividing 8, the number of plants/heat needed to equal a temp/greenery (also illustrated on the player boards), into the credit values for the temp and greenery standard projects.  
# 
# For energy, it was necessary to borrow some information from one of the expansions: _Colonies_. In order to trade with a colony, players must spend either 9 credits, 3 titanium, or 3 energy. This suggests that 1 energy = 1 titanium = 3 credits.  
# 
# Drawing a card is valued at 4 credits, combining the price to buy a card (3 credits) with the 1 credit gained from discarding it using the "Sell patents" standard project.

# variable definitions

income = 0
vp = 0
TR = vp + income

# standard projects
temp = 14
ocean = 18
greenery = 23
def city(income):
	return 25 - income
oxygen = greenery / 2

# resources
credit = 1
steel = 2
titanium = 3
plant = greenery / 8
heat = temp / 8
energy = 3
draw = 4

# production
def CREDIT(income):
	return income
def STEEL(income):
	return 2 * income
def TITANIUM(income):
	return 3 * income
def PLANT(income):
	return (greenery/8) * income
def ENERGY(income):
	return 3 * income
def HEAT(income):
	return (temp/8) * income

vars_dict_static = {'temp':temp, 'ocean':ocean, 'greenery':greenery, 'credit':credit, 'steel':steel,
             		'titanium':titanium, 'plant':plant, 'heat':heat, 'energy':energy, 'draw':draw}

vars_dict_variable = {'city':city, 'CREDIT':CREDIT, 'STEEL':STEEL, 'TITANIUM':TITANIUM,
                      'PLANT':PLANT, 'ENERGY':ENERGY, 'HEAT':HEAT}


# Victory points (VP) must also be converted to credits. To do this, the three terraforming standard projects were used. Since they confer a terraforming rating (TR) and not a victory point, the extra income from the TR must be subtracted from the cost of the project. This means that similar to the cards themselves, the value of a VP changes over time.
# 
# To come to a single value for a given generation and player count, the "points per credit" are determined for each of the three standard terraforming projects and then the average is taken. Note that greeneries are worth two points (one for the TR from raising the oxygen, another from the greenery tile itself) and so are calculated accordingly.

# define credits per victory point
def credits_per_vp(generation, player_count):
    for players in lastgens:
        if str(player_count) in players:
            lastgen = lastgens[players]
    income = lastgen - generation
    temp_ppc = 1/(temp - income) # ppc = points per credit
    ocean_ppc = 1/(ocean - income)
    greenery_ppc = 2/(greenery - income)
    ppc = (temp_ppc + ocean_ppc + greenery_ppc)/4
    vp = 1/ppc
    return vp

# numbers of credits per victory point for each player count and median generation
# X players, quarter N, credits per point
gen_credits_per_vp = {'2pq1cpp':credits_per_vp(2, 2),
                      '2pq2cpp':credits_per_vp(5, 2),
                      '2pq3cpp':credits_per_vp(8, 2),
                      '2pq4cpp':credits_per_vp(11, 2),
                      '3pq1cpp':credits_per_vp(1, 3),
                      '3pq2cpp':credits_per_vp(4, 3),
                      '3pq3cpp':credits_per_vp(7, 3),
                      '3pq4cpp':credits_per_vp(10, 3),
                      '4pq1cpp':credits_per_vp(1, 4),
                      '4pq2cpp':credits_per_vp(4, 4),
                      '4pq3cpp':credits_per_vp(6, 4),
                      '4pq4cpp':credits_per_vp(9, 4),
                      '5pq1cpp':credits_per_vp(1, 5),
                      '5pq2cpp':credits_per_vp(4, 5),
                      '5pq3cpp':credits_per_vp(6, 5),
                      '5pq4cpp':credits_per_vp(9, 5)
                     }

keys2pcpp = ['2pq1cpp', '2pq2cpp', '2pq3cpp', '2pq4cpp']
keys3pcpp = ['3pq1cpp', '3pq2cpp', '3pq3cpp', '3pq4cpp']
keys4pcpp = ['4pq1cpp', '4pq2cpp', '4pq3cpp', '4pq4cpp']
keys5pcpp = ['5pq1cpp', '5pq2cpp', '5pq3cpp', '5pq4cpp']

# determine number of remaining generations
def remgen(generation, player_count):
    global income
    for players in lastgens:
        if str(player_count) in players:
            lastgen = lastgens[players]
    income = lastgen - generation
    return income

#run above functions and determine credits per TR
def initialize(generation, player_count):
    income = remgen(generation, player_count)
    vp = credits_per_vp(generation, player_count)
    TR = vp + income
    return income, vp, TR

# chance to draw each tag

# Earth
earth_tags = base_cards[base_cards.Tags.str.contains('earth', na=False)]
chance_earth = len(earth_tags) / len(base_cards)
# Science
science_tags = base_cards[base_cards.Tags.str.contains('science', na=False)]
chance_science = len(science_tags) / len(base_cards)
# Plant
plant_tags = base_cards[base_cards.Tags.str.contains('plant', na=False)]
chance_plant = len(plant_tags) / len(base_cards)
# Microbe
microbe_tags = base_cards[base_cards.Tags.str.contains('microbe', na=False)]
chance_microbe = len(microbe_tags) / len(base_cards)
# Animal
animal_tags = base_cards[base_cards.Tags.str.contains('animal', na=False)]
chance_animal = len(animal_tags) / len(base_cards)
# Space
space_tags = base_cards[base_cards.Tags.str.contains('space', na=False)]
chance_space = len(space_tags) / len(base_cards)
# Event
event_tags = base_cards[base_cards.Tags.str.contains('event', na=False)]
chance_event = len(event_tags) / len(base_cards)
# Building
building_tags = base_cards[base_cards.Tags.str.contains('building', na=False)]
chance_building = len(building_tags) / len(base_cards)
# Jovian
jovian_tags = base_cards[base_cards.Tags.str.contains('jovian', na=False)]
chance_jovian = len(jovian_tags) / len(base_cards)
# Power
power_tags = base_cards[base_cards.Tags.str.contains('power', na=False)]
chance_power = len(power_tags) / len(base_cards)
# City
city_tags = base_cards[base_cards.Tags.str.contains('city', na=False)]
chance_city = len(city_tags) / len(base_cards)

tags_dict = {'earth':chance_earth, 'science':chance_science, 'plant':chance_plant, 
			 'microbe':chance_microbe, 'animal':chance_animal, 'space':chance_space,
             'event':chance_event, 'building':chance_building, 'jovian':chance_jovian,
             'power':chance_power, 'city':chance_city}

# #### Tile placement
# 
# Placing a tile on an area with resources allows the player to take those resources, adding to the value of the tile. To determine the average value added from these map resources, the total sum of credits gained from all of the resources on the map are divided by the total number of areas. This is done separately for ocean areas and non-ocean areas. The two off-world areas and the Noctis City area have been disregarded, since they cannot be placed upon except for unique circumstances.
# 
# <img src="https://4.bp.blogspot.com/-KVleOqhdyg0/XBxty1rpALI/AAAAAAAAFac/iJsDNEW0SDw6gTK2aHIS0oLc9px5XvzjQCEwYBhgL/s1600/TM%2BOriginal-Mars%2BOnly.jpg" alt="TM map" width="500"/>

#determine added value from gained resources when placing a tile

tile_land = (
            (2*steel * 3 +
            draw * 3 +
            steel * 3 +
            plant + titanium +
            plant * 10 +
            2*plant * 7 +
            titanium)
            / 48)

tile_ocean = (
             (2*steel +
             draw +
             plant * 3 +
             2*plant * 4 +
             2*titanium)
             / 12)

# #### Microbes  
# The following cards are taken into account when calculating the value of a microbe:
# * Ants - 1 vp per 2 microbes  
# * Decomposers - 1 vp per 3 microbes  
# * GHG Producing Bacteria - 1 temp per 2 microbes  
# * Nitrite Reducing Bacteria - 1 TR per 3 microbes  
# * Regolith Eaters - 1 oxygen per 2 microbes  
# * Tardigrades - 1 vp per 4 microbes  

# microbe value
# microbe_tags = base_cards[base_cards.Tags.str.contains('microbe', na=False)]
# display(microbe_tags)

def microbe_val(generation, player_count):
    income, vp, TR = initialize(generation, player_count)
    
    ants = vp / 2
    decomposers = vp / 3
    ghg_producing_bacteria = temp / 2
    nitrite_reducing_bacteria = TR / 3
    regolith_eaters = greenery / 4
    tardigrades = vp / 4
    
    microbes_list = [ants, decomposers, ghg_producing_bacteria, nitrite_reducing_bacteria,
                     regolith_eaters, tardigrades]
    microbe = sum(microbes_list) / len(microbes_list)
    return microbe

# #### Animals
# 
# The following cards are taken into account when calculating the value of an animal:  
# * Birds - 1 vp per animal
# * Fish - 1 vp per animal
# * Livestock - 1 vp per animal
# * Predators - 1 vp per animal
# * Ecological Zone - 1 vp per 2 animals
# * Herbivores - 1 vp per 2 animals
# * Pets - 1 vp per 2 animals
# * Small Animals - 1 vp per 2 animals

# animal value
# animal_tags = base_cards[base_cards.Tags.str.contains('animal', na=False)]
# display(animal_tags)

def animal_val(generation, player_count):
    income, vp, TR = initialize(generation, player_count)
    
    birds= fish= livestock= predators = vp
    ecological_zone= herbivores= pets= small_animals = vp/2
    
    animals_list = [birds, fish, livestock, predators, ecological_zone,
                    herbivores, pets, small_animals]
    animal = sum(animals_list) / len(animals_list)
    return animal

# #### Number of cities played
# 
# The average number of cities played in a game is set at 11. This is derived as a result of personal experience through dozens of games (mostly 2-player) as well as a rough averaging from the discussion [here](https://boardgamegeek.com/thread/1861021/how-many-cities)

cities_per_game = 11

def cities_current(generation, player_count):
    for players in lastgens:
        if str(player_count) in players:
            lastgen = lastgens[players]
    cities = (11 / lastgen) * generation
    return cities