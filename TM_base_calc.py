#!/usr/bin/env python
# coding: utf-8

import numpy as np
from statistics import median
import pandas as pd
import seaborn as sns
import csv
import ast
import re
import math

np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)

# create databases
base_cards = pd.read_csv('TM_base_project_list.csv')
all_games = pd.read_csv('games_list.csv')
base_games = all_games[(all_games.expansions == "['CORPORATE']") & (all_games.map == "THARSIS")]

# determine generation averages per player count
last_gen_2p = int(round(base_games[base_games.players == 2].generations.mean()))
last_gen_3p = int(round(base_games[base_games.players == 3].generations.mean()))
last_gen_4p = int(round(base_games[base_games.players == 4].generations.mean()))
last_gen_5p = int(round(base_games[base_games.players == 5].generations.mean()))

last_gens = {
            'last_gen_2p': int(round(base_games[base_games.players == 2].generations.mean())),
            'last_gen_3p': int(round(base_games[base_games.players == 3].generations.mean())),
            'last_gen_4p': int(round(base_games[base_games.players == 4].generations.mean())),
            'last_gen_5p': int(round(base_games[base_games.players == 5].generations.mean()))
           }

# average game length split into quarters with the median generation taken from each quarter
# X players, quarter N, median generation
gen_quarters = {
               '2p_q1_gen':round(last_gen_2p/4/2),
               '2p_q2_gen':round(last_gen_2p/4/2 + last_gen_2p/4),
               '2p_q3_gen':round(last_gen_2p/4/2 + last_gen_2p/4*2),
               '2p_q4_gen':round(last_gen_2p/4/2 + last_gen_2p/4*3),
               '3p_q1_gen':round(last_gen_3p/4/2),
               '3p_q2_gen':round(last_gen_3p/4/2 + last_gen_3p/4),
               '3p_q3_gen':round(last_gen_3p/4/2 + last_gen_3p/4*2),
               '3p_q4_gen':round(last_gen_3p/4/2 + last_gen_3p/4*3),
               '4p_q1_gen':round(last_gen_4p/4/2),
               '4p_q2_gen':round(last_gen_4p/4/2 + last_gen_4p/4),
               '4p_q3_gen':round(last_gen_4p/4/2 + last_gen_4p/4*2),
               '4p_q4_gen':round(last_gen_4p/4/2 + last_gen_4p/4*3),
               '5p_q1_gen':round(last_gen_5p/4/2),
               '5p_q2_gen':round(last_gen_5p/4/2 + last_gen_5p/4),
               '5p_q3_gen':round(last_gen_5p/4/2 + last_gen_5p/4*2),
               '5p_q4_gen':round(last_gen_5p/4/2 + last_gen_5p/4*3)
              }
keys_2p_gen = ['2p_q1_gen', '2p_q2_gen', '2p_q3_gen', '2p_q4_gen']
keys_3p_gen = ['3p_q1_gen', '3p_q2_gen', '3p_q3_gen', '3p_q4_gen']
keys_4p_gen = ['4p_q1_gen', '4p_q2_gen', '4p_q3_gen', '4p_q4_gen']
keys_5p_gen = ['5p_q1_gen', '5p_q2_gen', '5p_q3_gen', '5p_q4_gen']

# variable definitions

income = 0
vp = 0
TR = vp + income

# standard projects
temp = 14
ocean = 18
greenery = 23
def city(income):
    return 25 - (income + 1)
oxygen = TR

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
    return income + 1
def STEEL(income):
    return 2 * income
def TITANIUM(income):
    return 3 * income
def PLANT(income):
    return greenery/8 * (income + 1)
def ENERGY(income):
    return 3 * income
def HEAT(income):
    return (temp/8) * income

vars_dict_static = {'temp':temp, 'ocean':ocean, 'greenery':greenery, 'credit':credit, 'steel':steel, 
                    'titanium':titanium, 'plant':plant, 'heat':heat, 'energy':energy, 'draw':draw}

vars_dict_variable = {'city':city, 'CREDIT':CREDIT, 'STEEL':STEEL, 'TITANIUM':TITANIUM, 
                      'PLANT':PLANT, 'ENERGY':ENERGY, 'HEAT':HEAT}

vars_dict_resource = {}

# determine number of remaining generations
def remgen(generation, player_count):
    global income
    for players in last_gens:
        if str(player_count) in players:
            last_gen = last_gens[players]
    income = last_gen - generation
    return income, last_gen

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

# define credits per victory point
def credits_per_vp(generation, player_count):
    income, last_gen = remgen(generation, player_count)
    temp_ppc = 1/(temp - income) # ppc = points per credit
    ocean_ppc = 1/(ocean - income - tile_ocean)
    greenery_ppc = 2/(greenery - income - tile_land)
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

#run above functions and determine credits per TR
def initialize(generation, player_count):
    income, last_gen = remgen(generation, player_count)
    vp = credits_per_vp(generation, player_count)
    TR = vp + income
    return income, vp, TR, last_gen

# chance to draw each tag

# Earth
earth_tags = base_cards[base_cards.Tags.str.contains('earth', na=False)]
chance_earth_played = len(earth_tags) / len(base_cards)
chance_earth_showing = len(earth_tags[~earth_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)
# Science
science_tags = base_cards[base_cards.Tags.str.contains('science', na=False)]
chance_science_played = len(science_tags) / len(base_cards)
chance_science_showing = len(science_tags[~science_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)
# Plant
plant_tags = base_cards[base_cards.Tags.str.contains('plant', na=False)]
chance_plant_played = len(plant_tags) / len(base_cards)
chance_plant_showing = len(plant_tags[~plant_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)
# Microbe
microbe_tags = base_cards[base_cards.Tags.str.contains('microbe', na=False)]
chance_microbe_played = len(microbe_tags) / len(base_cards)
chance_microbe_showing = len(microbe_tags[~microbe_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)
# Animal
animal_tags = base_cards[base_cards.Tags.str.contains('animal', na=False)]
chance_animal_played = len(animal_tags) / len(base_cards)
chance_animal_showing = len(animal_tags[~animal_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)
# Space
space_tags = base_cards[base_cards.Tags.str.contains('space', na=False)]
chance_space_played = len(space_tags) / len(base_cards)
chance_space_showing = len(space_tags[~space_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)
# Event
event_tags = base_cards[base_cards.Tags.str.contains('event', na=False)]
chance_event_played = len(event_tags) / len(base_cards)

# Building
building_tags = base_cards[base_cards.Tags.str.contains('building', na=False)]
chance_building_played = len(building_tags) / len(base_cards)
chance_building_showing = len(building_tags[~building_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)
# Jovian
jovian_tags = base_cards[base_cards.Tags.str.contains('jovian', na=False)]
chance_jovian_played = len(jovian_tags) / len(base_cards)
chance_jovian_showing = len(jovian_tags[~jovian_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)
# Power
power_tags = base_cards[base_cards.Tags.str.contains('power', na=False)]
chance_power_played = len(power_tags) / len(base_cards)
chance_power_showing = len(power_tags[~power_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)
# City
city_tags = base_cards[base_cards.Tags.str.contains('city', na=False)]
chance_city_played = len(city_tags) / len(base_cards)
chance_city_showing = len(city_tags[~city_tags.Tags.str.contains('event', na=False)]) \
                       / len(base_cards)

tags_played_dict = {'earth':chance_earth_played, 'science':chance_science_played, 
                    'plant':chance_plant_played, 'microbe':chance_microbe_played, 
                    'animal':chance_animal_played, 'space':chance_space_played,
                    'event':chance_event_played, 'building':chance_building_played, 
                    'jovian':chance_jovian_played,'power':chance_power_played, 
                    'city':chance_city_played}

tags_showing_dict = {'earth':chance_earth_showing, 'science':chance_science_showing, 
                    'plant':chance_plant_showing, 'microbe':chance_microbe_showing, 
                    'animal':chance_animal_showing, 'space':chance_space_showing,
                    'event':chance_event_played, 'building':chance_building_showing, 
                    'jovian':chance_jovian_showing,'power':chance_power_showing, 
                     'city':chance_city_showing}

def cards_current(generation):
    return 10 + (4 * (generation - 1))

# microbe value
# microbe_tags = base_cards[base_cards.Tags.str.contains('microbe', na=False)]
# display(microbe_tags)

def microbe_val(generation, player_count):
    income, vp, TR, last_gen = initialize(generation, player_count)
    
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

vars_dict_resource.update({'microbe':microbe_val})

# animal value
# animal_tags = base_cards[base_cards.Tags.str.contains('animal', na=False)]
# display(animal_tags)

def animal_val(generation, player_count):
    income, vp, TR, last_gen = initialize(generation, player_count)
    
    birds= fish= livestock= predators = vp
    ecological_zone= herbivores= pets= small_animals = vp/2
    
    animals_list = [birds, fish, livestock, predators, ecological_zone,
                    herbivores, pets, small_animals]
    animal = sum(animals_list) / len(animals_list)
    return animal

vars_dict_resource.update({'animal':animal_val})

cities_per_game = 11
Mars_cities_per_game = 10

def cities_current(generation, player_count):
    for players in last_gens:
        if str(player_count) in players:
            last_gen = last_gens[players]
    cities = (11 / last_gen) * generation
    return cities

def Mars_cities_current(generation, player_count):
    for players in last_gens:
        if str(player_count) in players:
            last_gen = last_gens[players]
    Mars_cities = (10 / last_gen) * generation
    return Mars_cities

# define special case cards to be left out of the main function
special_cases = ['Adaptation Technology', 'Advanced Alloys', 'Anti-Gravity Technology', 'Ants', 
                 'Arctic Algae', 'Business Network', 'Capital', 'CEO’s Favorite Project', 
                 'Commercial District', 'Decomposers', 'Earth Catapult', 'Earth Office', 
                 'Ecological Zone', 
                 'Ganymede Colony', 'GHG Producing Bacteria', 'Herbivores', 'Immigrant City', 
                 'Immigration Shuttles', 
                 'Indentured Workers', 'Insulation', 'Inventor’s Guild', 'Io Mining Industries', 
                 'Land Claim', 
                 'Lava Flows', 'Mars University', 'Martian Rails', 'Mass Converter', 'Media Group', 
                 'Mining Area', 'Mining Rights', 'Nitrite Reducing Bacteria', 
                 'Nitrogen-Rich Asteroid', 'Noctis City', 'Olympus Conference', 'Optimal Aerobraking', 
                 'Pets', 'Phobos Space Haven', 'Power Infrastructure',
                 'Predators', 'Protected Habitat', 'Quantum Extractor', 'Regolith Eaters', 
                 'Research Outpost', 
                 'Robotic Workforce', 'Rover Construction', 'Search for Life', 'Shuttles', 
                 'Space Station', 'Special Design', 
                 'Standard Technology', 'Viral Enhancers', 'Water Import from Europa']

base_cases = base_cards[~base_cards.Title.isin(special_cases)].copy().reset_index(drop=True)

# main value calculation function
def is_null(x):
    return x is None or (isinstance(x, float) and math.isnan(x))


def compute_additional_cost_value(add_cost, generation, player_count):
    if is_null(add_cost):
        return 0
    value = 0
    for idx, ele in enumerate(add_cost.split(',')):
        add_cost_list = ele.strip().split(' ')
        value -= vars_scan(add_cost_list, generation, player_count)
    return value


def compute_victory_points_value(victory, vp):
    if is_null(victory) or not victory.isdigit():
        return 0
    return int(victory) * vp


def compute_immediate_benefit_value(i_benefit, generation, player_count):
    if is_null(i_benefit):
        return 0

    value = 0

    for idx, ele in enumerate(i_benefit.split(',')):
        i_benefit_list = ele.strip().split(' ')

        # for benefits dependent on the amount of another variable
        if 'per' in i_benefit_list:
            value += pers(i_benefit_list, generation, player_count)

        # for benefits with a choice; the larger of the two values is taken
        elif 'or' in i_benefit_list:
            value += ors((' ').join(i_benefit_list), generation, player_count)

        # for ocean and greenery tiles played on the opposite site
        elif 'land' in i_benefit_list and 'ocean' in i_benefit_list:
            value += ocean + tile_land - tile_ocean
        elif 'ocean' in i_benefit_list and 'greenery' in i_benefit_list:
            value += greenery + tile_ocean - tile_land

        # for special tiles
        elif 'special' in i_benefit_list:
            if 'ocean' in i_benefit_list:
                value += tile_ocean
            else:
                value += tile_land

         # for simple added values
        else:
            value += vars_scan(i_benefit_list, generation, player_count)

    return value


def compute_active_cost_benefit_value(a_cost, a_benefit, victory, generation, last_gen, player_count):
    if is_null(a_cost) or is_null(a_benefit):
        # Note: If one is null then the other must also be null
        return 0

    value = 0
    current_gen = generation

    while current_gen <= last_gen:
        # Cost
        cost = 0
        act_cost_list = a_cost.split(' ')
        if 'or' in a_cost:
            cost = ors(a_cost, current_gen, player_count, cost=True)
        else:
            is_variable_benefit = any(
                x for x in a_benefit.split(' ') if x in vars_dict_variable
            )
            if not is_variable_benefit or (is_variable_benefit and current_gen < last_gen):
                cost = vars_scan(act_cost_list, current_gen, player_count)

        # Benefit
        benefit = 0
        for benefit_list in a_benefit.split(','):
            benefit_list_split = benefit_list.strip().split(' ')
            if 'or' in benefit_list:
                benefit += ors(benefit_list, current_gen, player_count)
            elif 'on card' in benefit_list:
                number = (int(victory[0]) / int(victory[6])) * int(benefit_list[0])
                current_vp = credits_per_vp(current_gen, player_count)
                benefit += number * current_vp
            else:
                variable_eles = set(vars_dict_variable) & {'CREDIT', 'PLANT'}
                is_variable_benefit = any(x for x in benefit_list_split if x in variable_eles)
                if not is_variable_benefit or (is_variable_benefit and current_gen < last_gen):
                    # ensures increased production on the final turn isn't converted into points
                    benefit += vars_scan(benefit_list_split, current_gen, player_count)

        if cost < benefit:
            value += benefit - cost

        current_gen += 1

    return value


def compute_removal_value(removed, generation, player_count):
    if is_null(removed):
        return 0
    
    value = 0
    
    if 'or' in removed:
        value += ors(removed, generation, player_count)
    else:
        value += vars_scan(removed.split(' '), generation, player_count)
    return value


def base_value(func):
    def wrapper(database, generation, player_count):
        def compute_value(row):
            income, vp, TR, last_gen = initialize(generation, player_count)
            
            # Primary Cost
            value = -row.at['Primary_Cost']

            # Additional Cost
            add_cost = row.at['Additional_Cost']
            value += compute_additional_cost_value(add_cost, generation, player_count)

            # Victory Points
            victory = row.at['Victory_Points']
            value += compute_victory_points_value(victory, vp)

            # Immediate Benefit
            i_benefit = row.at['Immediate_Benefit']
            value += compute_immediate_benefit_value(i_benefit, generation, player_count)
            
            # Passive Benefit
            p_benefit = row.at['Passive_Benefit']

            # Active Cost/Benefit
            a_cost = row.at['Active_Cost']
            a_benefit = row.at['Active_Benefit']
            value += compute_active_cost_benefit_value(a_cost, a_benefit, victory, generation, last_gen, player_count)

            # Removed from Opponent
            removed = row.at['Removed_from_Opponent']
            value += compute_removal_value(removed, generation, player_count)

            # Special Cases
            value += func(database, generation, player_count, row, last_gen)
            
            return round(value)
    
        new_database = database
        new_database['Value'] = database.apply(compute_value, axis=1)
        new_database['Generation'] = generation
        new_database['Players'] = player_count
            
        return new_database
    return wrapper
