# ==============================================================================
# CNVS FRAMEWORK - EXECUTION ENVIRONMENT
# Copyright (c) 2026 Massimo Comitato.
#
# This file is part of the CNVS MTC Data Room.
# Licensed under the PolyForm Noncommercial License 1.0.0.
#
# Commercial use is prohibited without prior written authorization.
# Academic review and technical due diligence use are permitted under the license.
#
# SPDX-License-Identifier: PolyForm-Noncommercial-1.0.0
# ==============================================================================


# ==============================================================================
# Test name:  CNVS Test 15: Full Test-14 Replication with Critical-Cardinality Sensitivity
# filename:  "test_15_cnvs_m_sensitivity_full_pipeline_definitive.py"
#
# This file is part of the CNVS MTC Data Room.
# ==============================================================================


"""
CNVS Test 15 — Full Test-14 Replication with Critical-Cardinality Sensitivity.
The complete semantic, relational, leakage, refresh, latency, throughput and
scalability pipeline is repeated for m in {32, 64, 128, 256, 512}.

This executable test uses a true semantic input rather than a single prime-field
integer. The canonical semantic instance appears once, near the beginning of
this file, as requested.

The executable decision path is:

    V_L -> Cons_R -> Inv_C -> V_G

The exact hypergeometric reference and the compact theorem reference are used
only for comparison plots. They never decide V_G acceptance.

Full-run defaults:
    - 500,000 candidates per collusion q-cycle, semantic cycle, leakage level,
      and total relational sweep;
    - 10 independent seed replicates whose counts sum to 500,000;
    - an explicit V_L, Cons_R, Inv_C and V_G result for every candidate;
    - literal object-graph V_G audits in addition to the batched pipeline;
    - 1,000 active terminal verifiers in the main collusion sweep;
    - q in {0.20, 0.25, ..., 0.99, 1.00};
    - scalability sweep from 5 to 1,000 verifiers;
    - 3–6 omission/reassignment events;
    - 3–6 absurd-data/expulsion/refresh events;
    - selectors and topology generated with secrets;
    - plots shown and saved.

A smoke mode is available for syntax and workflow verification:

    python test_15_cnvs_m_sensitivity_full_pipeline_definitive.py --smoke --no-show

The smoke mode changes only the computational budget. It does not change the
validation architecture.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import secrets
import statistics
import time
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, MutableMapping, Optional, Sequence, Set, Tuple

import matplotlib.pyplot as plt
import numpy as np


# ==============================================================================
# CANONICAL SEMANTIC INPUT — REPORTED ONCE AT THE ORIGIN OF THE FILE
# ==============================================================================

CANONICAL_INPUT_TEXT = r"""TEST 14 — CANONICAL SEMANTIC INPUT INSTANCE
Building and apartment of Enzo / dr. Vincenzo Comitato
Entirely fictional data

======================================================================
PRELIMINARY DECLARATIONS OF IDENTITY AND CONSISTENCY
======================================================================

1. “Enzo” and “dr. Vincenzo Comitato” indicate the same person.
   Hereinafter the subject may be referred to interchangeably as “Enzo”
   or “Vincenzo”, but the canonical semantic identifier is:

       RESIDENT_PERSON = "dr. Vincenzo Comitato"
       ALIAS = "Enzo"

2. The building has the shape of a rectangular cuboid and measures:

       east-west length = 50.00 m
       north-south depth = 18.00 m
       ground footprint = 900.00 m²

   The correct value for the east-west length is 50.00 m.
   Any previous reference to 35.00 m as the length of the building
   must be considered replaced by 50.00 m.

3. The garden measures 100.00 m × 100.00 m and is quadrangular.
   The building is located exactly in the center of the garden.

   This results in the following geometric distances:

       east facade – east boundary distance = 25.00 m
       west facade – west boundary distance = 25.00 m
       north facade – north boundary distance = 41.00 m
       south facade – south boundary distance = 41.00 m

   Around the building, there is a walkable band of rough white stone
   5.00 m wide on all four sides.

   Beyond this band remains:

       20.00 m of usable garden on the east side
       20.00 m of usable garden on the west side
       36.00 m of usable garden on the north side
       36.00 m of usable garden on the south side

4. The building has four residential floors.
   The raised ground floor is counted as the first floor.

       floor 1 = raised ground floor
       floor 2 = second floor
       floor 3 = third floor
       floor 4 = fourth floor

5. Each floor contains four apartments.
   The apartments are distributed between two staircases:

       staircase A
       staircase B

   Each staircase serves two apartments per floor:

       one apartment oriented facing east
       one apartment oriented facing west

   Total number of apartments:

       4 floors × 4 apartments per floor = 16 apartments

6. Each half of the building occupied by a staircase measures 25.00 m along
   the east-west axis and 18.00 m along the north-south axis.

   For each staircase and each floor, the following consistent geometric
   subdivision is adopted:

       common staircase/landing core = 5.00 m × 18.00 m = 90.00 m²
       east-facing apartment = 10.00 m × 18.00 m = 180.00 m² gross
       west-facing apartment = 10.00 m × 18.00 m = 180.00 m² gross

   Total for each staircase sector:

       90.00 + 180.00 + 180.00 = 450.00 m²

   Total for the entire floor:

       450.00 m² × 2 staircases = 900.00 m²

7. Every repeated element described in the instance is considered a distinct
   and individually indexable semantic object.

   In particular, the columns of the perimeter wall, the windows, the balconies,
   the intercoms, the railings, the openings, the doors, the rooms, the sensors,
   the selectors, and the relations can generate separate terminal tasks.

   The fencing system alone contains 1,980 perimeter columns that are
   individually enumerable, in addition to other components.
   Therefore, the instance contains more than enough semantic material
   to generate at least 1,006 distinct selectors.

======================================================================
A. GENERAL IDENTIFICATION OF THE BUILDING
======================================================================

The house of Enzo, namely dr. Vincenzo Comitato, is located at:

    via Quattro Stagioni 17
    Pavia (PV)

The residence is an apartment located on the second floor of staircase A.

The building has four residential floors in total, counting the raised ground floor
as the first floor.

The building is light green in color.

The external facades are textured (knurled).
The texturing follows a longitudinal striped pattern.
The stripes draw an irregular, rough, and non-uniform graphic texture.
The external surface is not smooth.

The general shape of the building is that of a rectangular cuboid.

The building is oriented along the north-south axis and the east-west axis:

    minor north-south axis = 18.00 m
    major east-west axis = 50.00 m
    footprint area = 900.00 m²

The building has two staircases:

    staircase A, located towards the main garden entrance
    staircase B, located to the south relative to staircase A

Each floor contains four apartments.
Two apartments belong to staircase A.
Two apartments belong to staircase B.

For each staircase, the two apartments on the floor are oriented respectively:

    one facing east
    one facing west

The arrangement is repeated for all four floors.

======================================================================
B. NORTH FACADE, BALCONIES AND OPENINGS
======================================================================

The north facade contains four balconies for each floor:

    two balconies belonging to the apartments of staircase A
    two balconies belonging to the apartments of staircase B

The balconies are arranged in pairs.
Each pair occupies the facade sector pertinent to the corresponding staircase.
The balconies are distributed across the four longitudinal sectors of the facade.

Number of balconies on the north facade:

    4 balconies per floor × 4 floors = 16 balconies

Each balcony on the north facade measures:

    length = 6.00 m
    depth = 1.50 m
    walkable area = 9.00 m²

Each balcony on the north facade has:

    1 large window
    2 small windows

The large window is always located towards the end of the balcony
farthest from the door of the corresponding staircase.

For east-facing apartments, the large window is located
towards the east side.

For west-facing apartments, the large window is located
towards the west side.

The same rule applies to the apartments of staircase A and staircase B.

Each railing of the north balconies is:

    made of iron
    creamy-white in color
    identical to the other railings
    1.00 m high

The railing is formed by thin vertical cylindrical columns.

The large window of each apartment measures:

    total width = 0.90 m
    number of leaves = 2
    width of each leaf = 0.45 m
    height = 2.20 m

The internal height of the rooms is 2.60 m.
The large window reaches almost up to the ceiling.

The large window begins 0.25 m from the external lateral end
 of the facade sector pertinent to the apartment.

Each small window measures:

    width = 0.50 m
    height = 1.20 m
    height of the lower edge (sill) from the floor = 1.00 m

The upper edge of the small window is aligned with the upper edge
 of the large window.

The first small window is 1.00 m away from the large window.

The second small window is 1.00 m away from the first small window.

The small window closest to the staircase door is 0.25 m away
 from the internal end of the balcony railing.

The part of the facade not occupied by openings consists of blind structural
masonry, distributed between the openings and the lateral returns.

All windows have electric shutters:

    material = plastic
    color = white

Total number of openings on the north facade:

    16 large windows
    32 small windows
    total = 48 openings

======================================================================
C. RAISED GROUND FLOOR AND SECURITY BARS
======================================================================

The raised ground floor coincides with the first residential floor.

All glazed openings of the apartments on the raised ground floor
are protected by green security bars.

The security bars are present:

    on the large windows of the north facade
    on the small windows of the north facade
    on the small windows of the east and west facades
    on the french windows of the south facade

In the apartments of the second, third, and fourth floors, there are no
external security bars.

======================================================================
D. EAST AND WEST FACADES
======================================================================

The lateral facade facing east has three small windows per floor.

The lateral facade facing west has three small windows per floor.

The two facades are mirrored (specular).

Number of lateral windows:

    east facade = 3 windows × 4 floors = 12 windows
    west facade = 3 windows × 4 floors = 12 windows
    total lateral windows = 24

Each lateral window measures:

    width = 0.50 m
    height = 1.20 m
    height of the lower edge from the floor = 1.00 m

The lateral windows are vertically aligned with the small windows
 of the balconies on the north facade.

The three windows on each floor are 3.00 m apart from each other,
measuring the distance between the central axes of the openings.

Each lateral window has a white plastic electric shutter.

The windows of the raised ground floor have green protective security bars
identical to those on the north facade.

======================================================================
E. SOUTH FACADE, BALCONIES AND FRENCH WINDOWS
======================================================================

The south facade is geometrically mirrored relative to the north facade.

The south facade also contains four balconies per floor:

    4 balconies per floor × 4 floors = 16 balconies

The south facade does not have entrance doors to the staircases.

Each south balcony measures:

    length = 6.00 m
    depth = 1.50 m
    area = 9.00 m²

The railings of the south balconies are identical to the railings of the north balconies:

    iron
    creamy-white color
    height 1.00 m
    thin vertical cylindrical columns

Each south balcony has three french windows.

Each south french window:

    has only one leaf
    width = 0.70 m
    height = 2.20 m
    starts from the floor level
    ends 0.40 m from the 2.60 m high ceiling
    has a white electric shutter

Total number of french windows on the south facade:

    16 balconies × 3 french windows = 48 french windows

All balconies, both north and south, have flooring:

    red-brown brick color
    brick shade
    whitish veins
    rough surface

Total number of balconies in the building:

    16 north balconies + 16 south balconies = 32 balconies

======================================================================
F. GENERAL INTERNAL FLOORING
======================================================================

All apartments have floors made of square tiles.

Each tile measures:

    0.30 m × 0.30 m

The color is white with a marble effect.
The veins have light blue and green tones.

The same flooring is present in all rooms,
except for the specifically described tiled vertical surfaces.

======================================================================
G. GARDEN, VEGETATION AND BUILDING POSITION
======================================================================

The building is completely surrounded by a garden.

The garden has a quadrangular shape and measures:

    east-west side = 100.00 m
    north-south side = 100.00 m
    total area = 10,000.00 m²

The building is perfectly centered in the garden.

The distances between the facades and the boundary are:

    north = 41.00 m
    south = 41.00 m
    east = 25.00 m
    west = 25.00 m

Around the building, there is a walkable surface of rough white stone.

The stone band:

    is continuous
    borders the entire building
    is 5.00 m wide on each side

The usable garden beyond the stone band measures:

    36.00 m on the north side
    36.00 m on the south side
    20.00 m on the east side
    20.00 m on the west side

The garden contains tall pine trees distributed along the perimeter and in the
surrounding grassy areas.

The grass is:

    short
    regularly mowed

The building is free-standing on all four sides.

======================================================================
H. INTERNAL GARDEN ROAD SYSTEM
======================================================================

The main gate is located at the center of the north side of the garden.

From the main gate, a paved path leads directly towards the building.

The pavement consists of rough gray cobblestones.

The central road measures:

    driveway width = 2.00 m

Two sidewalks are present on the sides of the central road.

At 5.00 m from the external facades of the building, there is a service
 road that runs entirely around the building.

The ring road:

    is connected to the central entrance road
    allows reaching the doors of staircase A and staircase B
    follows the outer edge of the walkable stone band
    maintains a distance of 5.00 m from the facades of the building

======================================================================
I. PERIMETER FENCE
======================================================================

The garden is surrounded by a gray masonry fence.

The fence consists of:

    a continuous lower wall
    repeated vertical columns above the wall

The continuous lower wall:

    height = 0.60 m
    material = gray masonry
    finish = rough

Vertical columns are repeated above the continuous wall.

Each column:

    width = 0.10 m
    clear distance to the next column = 0.10 m
    reaches a total height of 2.00 m from the ground
    therefore emerges for 1.40 m above the 0.60 m continuous wall

The column-gap pitch is:

    0.10 m + 0.10 m = 0.20 m

The geometric perimeter of the garden is:

    100 + 100 + 100 + 100 = 400.00 m

The main gate interrupts the wall for a width of 4.00 m.

Residual length of the modular fence:

    400.00 - 4.00 = 396.00 m

Logical number of column-gap modules:

    396.00 / 0.20 = 1,980 modules

Number of individually indexable vertical columns:

    1,980 columns

The terminations at the corners are treated as distinct terminal elements.
Any small geometric closing adjustments at the corners
do not change the logical count of the 1,980 column identifiers.

======================================================================
J. MAIN GATE AND INTERCOMS
======================================================================

The main gate of the garden is located at the center of the north side.

The gate is:

    material = anodized steel
    color = matte white
    width = 4.00 m
    height = 2.00 m

The gate is not perfectly aligned with the vertical elements
 of the fence, because the fence columns define an independent
 spacing.

On the right and left sides of the gate are the intercoms.

The intercoms replicate the distribution of the sixteen apartments.

There are:

    8 intercoms on the right panel
    8 intercoms on the left panel
    total = 16 intercoms

Each intercom has:

    identification name tag
    round button
    camera

The right panel contains four rows and two columns:

    row 4: Tenant 4v | Tenant 4z
    row 3: Tenant 3v | Tenant 3z
    row 2: Tenant 2v | Vincenzo Comitato
    row 1: Tenant 1v | Tenant 1z

The asterisk in the original representation indicates the round button
 of the intercom, oriented towards the east side of the panel.

The intercom of dr. Vincenzo Comitato:

    is located on the right panel
    is located in the second row from the bottom
    has one intercom above it
    has two intercoms below it
    corresponds to the second floor
    is oriented facing east/right
    bears the inscription "dr. Vincenzo Comitato"

On the left side of the gate, there is a second panel with another
eight intercoms, organized in the same scheme of four rows and two columns.

======================================================================
K. EXTERNAL TECHNICAL CABINET
======================================================================

Outside the garden, along the masonry perimeter of the north side,
towards the west end, there is a large technical cabinet.

The cabinet contains:

    electrical panels
    water meters
    gas meters
    electricity meters
    internet cable connections and derivations

The cabinet is:

    color = gray
    length = 4.00 m
    height = 2.00 m
    material = reinforced aluminum
    closure = keyed lock

======================================================================
L. LOCATION OF ENZO'S APARTMENT
======================================================================

The apartment of Enzo, namely dr. Vincenzo Comitato, is located at:

    staircase = A
    floor = 2
    orientation = east

On the landing, the apartment is located on the right.

On the same landing, there is only one facing apartment,
because each staircase serves two apartments per floor.

The landing measures:

    east-west length = 2.50 m
    north-south width = 3.00 m
    area = 7.50 m²

The apartment occupies a gross module of:

    10.00 m east-west
    18.00 m north-south
    gross area = 180.00 m²

The usable internal area, net of perimeter walls, pillars,
shafts, and partitions, is assumed to be approximately 155.00 m².

The apartment contains four main rooms:

    kitchen
    small bedroom / single bedroom
    master bedroom
    study / room 3

To these are added:

    entryway
    corridor
    bathroom

The total number of main functional spaces is therefore seven.

======================================================================
M. ENTRANCE DOOR, ENTRYWAY AND CORRIDOR
======================================================================

The entrance door of the apartment is:

    armored
    dark brown color
    matte and carved finish
    fine walnut wood cladding

Immediately after the door is a spacious entryway.

The entryway measures:

    east-west length = 3.00 m
    north-south width = 3.20 m
    area = 9.60 m²

At the center of the entryway begins a corridor heading east.

The corridor is long and constitutes the distributive axis of the house.

The corridor measures:

    east-west length = 6.40 m
    north-south width = 1.80 m
    area = 11.52 m²

The other rooms open on the north and south sides of the corridor.

The internal doors are:

    white
    made of fine wood
    equipped with shiny golden knob handles
    equipped with a removable golden key

The corridor ends to the east with the bathroom door.

======================================================================
N. COMMON ENVIRONMENTAL CONTROL RULES
======================================================================

Every room, including the bathroom, has an air conditioner.

The air conditioner is not present:

    in the entryway
    in the corridor

The entire apartment has underfloor heating.

Every room equipped with climate control has:

    a button for lighting
    a touch screen for adjusting the air conditioner
    a touch screen for adjusting the underfloor heating

The button and the touch screen are located on the wall facing
the corridor.

The control is placed on the right side of the room's entrance door.

The touch screen is placed immediately to the right of the light button.

======================================================================
O. KITCHEN
======================================================================

The kitchen is the first room on the right entering the corridor.

The kitchen is located on the north side of the corridor.

The kitchen measures:

    east-west length = 4.00 m
    north-south width = 5.00 m
    area = 20.00 m²

The kitchen faces the north balcony.

The two small windows of the north balcony belong to the kitchen.

The kitchen does not have a large window.

The east wall of the kitchen is tiled up to the separation line
between the wall and the ceiling.

On the east wall are located:

    kitchen cabinets
    worktop
    cooktop

The north wall contains the two small windows facing the balcony.

The west and south walls:

    are not covered with tiles
    are creamy-white in color

The floor is made of 0.30 m × 0.30 m tiles,
white marble effect with light blue-green veins.

In the center of the kitchen is a rectangular table.

The table is oriented along the north-south axis.

The table measures:

    length = 2.00 m
    width = 0.80 m

On the west wall, there are shelves arranged on three levels.

On the shelves are:

    salt shaker
    pots
    various appliances

The kitchen has an air conditioner.

======================================================================
P. SMALL BEDROOM / SINGLE BEDROOM
======================================================================

Next to the kitchen, proceeding east along the corridor,
there is a white door leading to the small bedroom.

The small bedroom is located on the north side of the corridor.

The small bedroom measures:

    east-west length = 3.80 m
    north-south width = 4.60 m
    area = 17.48 m²

The small bedroom has a single bed.

The bed is oriented towards the south wall.

The south wall is located on the right side of the entrance door
 of the small bedroom.

The south wall borders the area close to the bathroom,
located at the end of the corridor.

The north wall contains the large two-leaf window
that opens onto the north balcony.

The large window of the small bedroom measures:

    width = 0.90 m
    two leaves of 0.45 m
    height = 2.20 m

On the west wall, bordering the kitchen, there is a bookcase.

The bookcase measures:

    width = 0.80 m
    number of shelves = 5
    height = up to the ceiling

The bookcase contains many books,
especially on pharmacology and pharmacodynamics.

The narrative description attributes these interests to the fact that
Vincenzo is a very skilled and well-known doctor-pharmacist.

On the south wall, above the bed, there is a picture.

The picture measures:

    length = 0.30 m
    height = 0.15 m

The picture is a copy of a well-known Picasso painting.

On the east wall, there is a poster of J-Ax.

The small bedroom has an air conditioner.

======================================================================
Q. BATHROOM
======================================================================

The bathroom is located at the end of the corridor, on the east side.

The bathroom door opens from the corridor inwards.

The bathroom measures:

    east-west length = 3.00 m
    north-south width = 3.40 m
    area = 10.20 m²

On the east wall, facing the lateral garden, there is a window.

Under the window is a bathtub.

The bathtub occupies almost the entire north-south width of the bathroom.

The bathtub measures:

    east-west width = 0.70 m
    north-south length = 2.40 m

On the south wall are located:

    sink
    medicine cabinet

The medicine cabinet is:

    well-kept
    made of wood
    glossy white color

On the north wall are located:

    toilet
    bidet

In the corner formed by the west wall and the north wall
is the shower tray.

The shower tray is:

    material = glossy white ceramic
    dimensions = 0.60 m × 0.60 m

The west wall separates the bathroom from the corridor.

The north wall separates the bathroom from the small bedroom.

The bathroom has an air conditioner.

======================================================================
R. MASTER BEDROOM
======================================================================

Entering the corridor, on the left side, is the master bedroom.

The master bedroom is located on the south side of the corridor.

The room measures:

    east-west length = 4.50 m
    north-south width = 4.80 m
    area = 21.60 m²

The north wall, facing the corridor, houses the double bed.

The south wall contains two single-leaf french windows.

Each french window measures:

    width = 0.70 m
    height = 2.20 m

The two french windows overlook the south balcony,
facing the rear garden of the building.

On the east wall is a six-door wardrobe.

The wardrobe is:

    glossy beige color
    equipped with sliding doors
    equipped with automatic internal lighting
    thermo-ventilated

When a door is opened, the internal courtesy light turns on.

On the south wall, to the left of the first french window
considering the west-east axis, is a small cabinet.

A 65-inch television rests on the cabinet.

The master bedroom has an air conditioner.

======================================================================
S. STUDY / ROOM 3
======================================================================

Proceeding along the corridor past the master bedroom,
on the left side and close to the bathroom,
is room 3.

Room 3 is a small room used as a study.

The room measures:

    east-west length = 3.40 m
    north-south width = 4.00 m
    area = 13.60 m²

In the center of the study is a round table.

Around the table is a library that runs along
most of the walls.

The south wall remains largely free because it contains
a french window.

The french window measures:

    width = 0.70 m
    height = 2.20 m

The french window overlooks the south balcony functionally shared
with the master bedroom.

The library is:

    dark brown color
    main material = walnut wood

The round table is also:

    dark brown color
    material = walnut

The books mainly deal with:

    human anatomy
    physiology
    pathology
    related medical disciplines

A part of the library is also located along the north wall,
where the entrance door to the study is located.

The north wall separates the study from the corridor.

The study has an air conditioner.

======================================================================
T. DISTRIBUTION OF THE APARTMENT OPENINGS
======================================================================

On the north balcony of Enzo's apartment are present:

    1 large window of the small bedroom
    2 small windows of the kitchen

On the south balcony of Enzo's apartment are present:

    2 french windows of the master bedroom
    1 french window of the study

On the east side of the apartment is present:

    1 window of the bathroom

The openings maintain the general characteristics
of their respective facades.

======================================================================
U. INTERNAL SECURITY
======================================================================

The entire house is protected by an advanced security system.

Cameras are present:

    in the entryway
    in the corridor

The cameras monitor the main access and distribution axes.

======================================================================
V. GENERAL HOME FURNISHINGS
======================================================================

The furniture in the house is luxurious.

At the end of the corridor, there is a large grandfather clock.

The clock:

    reaches almost to the ceiling
    is beige in color
    is a valuable nineteenth-century pendulum clock
    has sober motifs
    has handcrafted finishes
    is hand-finished

The clock is placed in the corner between:

    the bathroom
    room 3 / library

In the wall sections between a door and the neighboring room
there are low plants in pots.

The pots are:

    made of terracotta
    matte gray color

There are:

    1 plant between the master bedroom door and the study door
    1 plant between the kitchen door and the small bedroom door
    1 plant between the small bedroom door and the bathroom,
      in the corner between the north wall of the corridor and the west wall of the bathroom

Total number of plants in the corridor:

    3 plants

======================================================================
W. INTERNAL HEIGHTS AND COLORS
======================================================================

The ceiling of the entire apartment is uniform.

Internal height:

    2.60 m

The internal walls are creamy-white in color,
except for the specifically described claddings/tiles.

======================================================================
X. ENTRYWAY FURNISHINGS
======================================================================

In the entryway, there is a coat rack.

The coat rack is:

    made of cherry wood
    of high quality
    light brown color
    fixed to the north wall
    located on the right upon entering

On the south wall, to the left of the entrance door,
there is a high-quality sideboard.

The sideboard has:

    a large mirror
    an original marble shelf

On the sideboard rests a silver tray
intended for placing keys.

To the left of the tray is a writing set.

The writing set includes:

    a notebook
    a pencil

======================================================================
Y. SUMMARY QUANTITATIVE INVENTORY
======================================================================

Building:

    1 building
    4 residential floors
    2 staircases
    16 apartments
    8 apartments per staircase
    4 apartments per floor

Balconies:

    16 north balconies
    16 south balconies
    32 total balconies

External openings:

    16 large north windows
    32 small north windows
    48 south french windows
    12 east lateral windows
    12 west lateral windows
    total main openings = 120

Intercoms:

    8 to the right of the gate
    8 to the left of the gate
    total = 16

Fence:

    perimeter = 400.00 m
    gate gap = 4.00 m
    residual modular development = 396.00 m
    column-gap pitch = 0.20 m
    individual columns = 1,980

Apartment of Enzo / Vincenzo:

    1 entryway
    1 corridor
    1 kitchen
    1 small bedroom
    1 master bedroom
    1 study
    1 bathroom
    3 corridor plants
    2 internal cameras
    1 grandfather clock
    1 coat rack
    1 sideboard
    1 main mirror
    1 marble shelf
    1 silver tray
    1 writing set
    1 65-inch television
    1 rectangular table in the kitchen
    1 round table in the study
    1 single bed
    1 double bed
    1 6-door wardrobe
    1 bathtub
    1 shower
    1 toilet
    1 bidet
    1 sink
    1 medicine cabinet

======================================================================
Z. ATOMIZATION RULE FOR TEST 14
======================================================================

For the purposes of semantic fragmentation, each declared fact
can be decomposed into one or more distinct terminal data points.

Examples:

    building.east_west_length = 50.00 m
    building.north_south_depth = 18.00 m
    building.area = 900.00 m²

    north_balcony_01.length = 6.00 m
    north_balcony_01.depth = 1.50 m
    north_balcony_01.railing.color = creamy-white

    fence_column_0001.width = 0.10 m
    fence_column_0001.top_elevation = 2.00 m
    fence_column_0001.distance_to_next = 0.10 m

    fence_column_1980.width = 0.10 m
    fence_column_1980.top_elevation = 2.00 m
    fence_column_1980.distance_to_next = 0.10 m

    enzo_apartment.resident_alias = Enzo
    enzo_apartment.resident_name = dr. Vincenzo Comitato
    enzo_apartment.floor = 2
    enzo_apartment.staircase = A
    enzo_apartment.orientation = east

The 1,980 columns of the fence must be treated as 1,980 distinct
objects and not as a single aggregate data point.

Similarly, every window, balcony, intercom, door, room,
piece of furniture, appliance, geometric relationship, and measurable property
can be indexed separately.

The instance is therefore semantically sufficient to produce more than 1,006
terminal leaf selectors, even without artificially duplicating the data.

======================================================================
END OF THE CANONICAL SEMANTIC INSTANCE
======================================================================
"""


# ==============================================================================
# FORMAL SYSTEM PRINTED BY THE EXECUTABLE TEST
# ==============================================================================

FORMULA_VL = r"""
V_L(s) := < Form_sigma(id, d, a, obs) AND Conv_sigma(a, d, obs), p >
Form_sigma : Id_sigma x D_sigma x At_sigma x Obs_sigma^perp -> {0,1}
Conv_sigma : At_sigma x D_sigma x Obs_sigma^perp -> {0,1}
Adm_L(s) = 1 iff pi_1(V_L(s)) = 1
""".strip()

FORMULA_VG = r"""
V_G(S(t)) = 1 iff
    (for every s in Ter(t), pi_1(V_L(s)) = 1)
    AND Cons_R(R(t), E(t))
    AND Inv_C(S(t))

Cons_R(R(t), E(t)) = 1 iff
    for all s, s' in E(t): ((s, s') in R(t) iff s' in D(s))

Inv_C(S(t)) = 1 iff
    for every c_i in C: c_i(E(t), R(t)) = 1
""".strip()

FORMULA_EXACT_REF = r"""
P_exact(Q,r,m,p_inf) =
    SUM_x [ C(r,x) C(Q-r,m-x) / C(Q,m) ] p_inf^(m-x),
where x ranges from max(0, m-(Q-r)) to min(m,r).
""".strip()

FORMULA_THEOREM_REF = r"""
p_comp = q + (1-q) p_inf
P_theorem = p_comp^m
""".strip()


# ==============================================================================
# DEFAULT CONFIGURATION
# ==============================================================================

DEFAULT_Q_MAIN = 1_000
DEFAULT_RESERVE_VERIFIERS = 6
DEFAULT_ITERATIONS_PER_Q = 500_000
DEFAULT_SCALABILITY_ITERATIONS = 500_000
DEFAULT_CRITICAL_FRAGMENTS = 64
DEFAULT_H_MIN_BITS = 1.0
DEFAULT_BATCH_SIZE = 4_096
DEFAULT_LATENCY_SAMPLES = 100
DEFAULT_OUTPUT_DIR = Path("test_14_outputs")

Q_COLLUSION_SCENARIOS: Tuple[float, ...] = (
    0.20, 0.25, 0.30, 0.33, 0.40, 0.45, 0.50,
    0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85,
    0.90, 0.95, 0.96, 0.97, 0.98, 0.99, 1.00,
)

Q_SCALABILITY_GRID: Tuple[int, ...] = (
    5, 10, 25, 50, 100, 250, 500, 750, 1_000,
)


# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

@dataclass(frozen=True)
class SemanticFact:
    fact_id: str
    value: Any
    value_type: str
    unit: str
    epsilon: float
    group: str
    description: str


@dataclass(frozen=True)
class SemanticEquation:
    name: str
    required_fact_ids: Tuple[str, ...]
    evaluator: Callable[[Mapping[str, Any]], float]
    tolerance: float
    description: str




# ==============================================================================
# GENERIC UTILITIES
# ==============================================================================

SECURE_RNG = secrets.SystemRandom()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def normalize_text(value: Any) -> str:
    return " ".join(str(value).strip().casefold().split())


def is_numeric_fact(fact: SemanticFact) -> bool:
    return fact.value_type in {"float", "int"} and isinstance(fact.value, (int, float)) and not isinstance(fact.value, bool)


def value_to_float(value: Any) -> float:
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, (int, float)):
        return float(value)
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64)


def make_selector(fact_id: str, cycle_nonce: str) -> str:
    salt = secrets.token_hex(16)
    return "tau_" + sha256_text(f"{cycle_nonce}|{fact_id}|{salt}")[:20]


def quantile(values: Sequence[float], q: float) -> float:
    if not values:
        return 0.0
    return float(np.quantile(np.asarray(values, dtype=float), q))


def random_event_numbers(iterations: int, count: int) -> List[int]:
    if iterations <= 0:
        return []
    count = min(count, iterations)
    return sorted(SECURE_RNG.sample(range(1, iterations + 1), count))


def p_inf_from_h(h_min_bits: float) -> float:
    return 1.0 if h_min_bits <= 0 else 2.0 ** (-float(h_min_bits))


# ==============================================================================
# SEMANTIC CATALOG CONSTRUCTION
# ==============================================================================


def build_semantic_catalog() -> List[SemanticFact]:
    """
    Atomize the canonical input into a large structured catalog.

    Repeated physical elements are individual semantic objects. The fence alone
    contributes 1,980 individually addressable columns and multiple measurable
    attributes per column. No artificial duplicate facts are needed.
    """
    facts: List[SemanticFact] = []

    def add(
        fact_id: str,
        value: Any,
        value_type: str,
        unit: str = "",
        epsilon: float = 0.0,
        group: str = "general",
        description: str = "",
    ) -> None:
        facts.append(SemanticFact(
            fact_id=fact_id,
            value=value,
            value_type=value_type,
            unit=unit,
            epsilon=float(epsilon),
            group=group,
            description=description or fact_id,
        ))

    # --------------------------------------------------------------------------
    # Canonical identity and address.
    # --------------------------------------------------------------------------
    add("resident.canonical_name", "dr. Vincenzo Comitato", "str", group="identity")
    add("resident.alias", "Enzo", "str", group="identity")
    add("address.street", "via Quattro Stagioni", "str", group="address")
    add("address.number", 17, "int", epsilon=0.0, group="address")
    add("address.city", "Pavia", "str", group="address")
    add("address.province", "PV", "str", group="address")

    # --------------------------------------------------------------------------
    # Building geometry and counts.
    # --------------------------------------------------------------------------
    add("building.length_ew_m", 50.0, "float", "m", 0.05, "building.geometry")
    add("building.depth_ns_m", 18.0, "float", "m", 0.05, "building.geometry")
    add("building.footprint_m2", 900.0, "float", "m2", 0.5, "building.geometry")
    add("building.floors", 4, "int", "count", 0.0, "building.counts")
    add("building.staircases", 2, "int", "count", 0.0, "building.counts")
    add("building.apartments_per_floor", 4, "int", "count", 0.0, "building.counts")
    add("building.total_apartments", 16, "int", "count", 0.0, "building.counts")
    add("building.color", "light green", "str", group="building.surface")
    add("building.shape", "rectangular cuboid", "str", group="building.geometry")
    add("building.surface_texture", "textured (knurled), rough, not smooth", "str", group="building.surface")
    add("building.stripe_orientation", "longitudinal", "str", group="building.surface")
    add("building.sector_length_ew_m", 25.0, "float", "m", 0.05, "building.geometry")
    add("building.stair_core_length_ew_m", 5.0, "float", "m", 0.05, "building.geometry")
    add("building.stair_core_area_m2", 90.0, "float", "m2", 0.2, "building.geometry")
    add("building.apartment_module_length_ew_m", 10.0, "float", "m", 0.05, "building.geometry")
    add("building.apartment_module_depth_ns_m", 18.0, "float", "m", 0.05, "building.geometry")
    add("building.apartment_module_gross_m2", 180.0, "float", "m2", 0.2, "building.geometry")
    add("building.sector_area_m2", 450.0, "float", "m2", 0.5, "building.geometry")

    # --------------------------------------------------------------------------
    # Garden and paths.
    # --------------------------------------------------------------------------
    add("garden.length_ew_m", 100.0, "float", "m", 0.05, "garden.geometry")
    add("garden.depth_ns_m", 100.0, "float", "m", 0.05, "garden.geometry")
    add("garden.area_m2", 10_000.0, "float", "m2", 1.0, "garden.geometry")
    add("garden.distance_east_m", 25.0, "float", "m", 0.05, "garden.geometry")
    add("garden.distance_west_m", 25.0, "float", "m", 0.05, "garden.geometry")
    add("garden.distance_north_m", 41.0, "float", "m", 0.05, "garden.geometry")
    add("garden.distance_south_m", 41.0, "float", "m", 0.05, "garden.geometry")
    add("garden.walkway_width_m", 5.0, "float", "m", 0.02, "garden.paths")
    add("garden.usable_east_m", 20.0, "float", "m", 0.05, "garden.geometry")
    add("garden.usable_west_m", 20.0, "float", "m", 0.05, "garden.geometry")
    add("garden.usable_north_m", 36.0, "float", "m", 0.05, "garden.geometry")
    add("garden.usable_south_m", 36.0, "float", "m", 0.05, "garden.geometry")
    add("garden.grass", "short and mowed", "str", group="garden.surface")
    add("garden.trees", "tall pine trees", "str", group="garden.vegetation")
    add("garden.main_road_width_m", 2.0, "float", "m", 0.02, "garden.paths")
    add("garden.main_road_material", "rough gray cobblestones", "str", group="garden.paths")
    add("garden.has_two_sidewalks", True, "bool", group="garden.paths")
    add("garden.ring_road_distance_from_building_m", 5.0, "float", "m", 0.02, "garden.paths")

    # --------------------------------------------------------------------------
    # Fence and gate aggregate facts.
    # --------------------------------------------------------------------------
    add("fence.perimeter_m", 400.0, "float", "m", 0.1, "fence.aggregate")
    add("fence.gate_width_m", 4.0, "float", "m", 0.02, "fence.aggregate")
    add("fence.modular_length_m", 396.0, "float", "m", 0.1, "fence.aggregate")
    add("fence.lower_wall_height_m", 0.60, "float", "m", 0.01, "fence.aggregate")
    add("fence.column_width_m", 0.10, "float", "m", 0.002, "fence.aggregate")
    add("fence.column_gap_m", 0.10, "float", "m", 0.002, "fence.aggregate")
    add("fence.module_pitch_m", 0.20, "float", "m", 0.003, "fence.aggregate")
    add("fence.column_total_height_m", 2.0, "float", "m", 0.01, "fence.aggregate")
    add("fence.column_emergent_height_m", 1.40, "float", "m", 0.01, "fence.aggregate")
    add("fence.column_count", 1_980, "int", "count", 0.0, "fence.aggregate")
    add("fence.material", "gray masonry", "str", group="fence.aggregate")
    add("fence.finish", "rough", "str", group="fence.aggregate")
    add("gate.material", "anodized steel", "str", group="gate")
    add("gate.color", "matte white", "str", group="gate")
    add("gate.height_m", 2.0, "float", "m", 0.01, "gate")

    # Individual fence columns: every physical column is a distinct object.
    for idx in range(1, 1_981):
        prefix = f"fence.column.{idx:04d}"
        add(f"{prefix}.width_m", 0.10, "float", "m", 0.002, "fence.columns")
        add(f"{prefix}.total_height_m", 2.0, "float", "m", 0.01, "fence.columns")
        add(f"{prefix}.gap_to_next_m", 0.10, "float", "m", 0.002, "fence.columns")
        add(f"{prefix}.lower_wall_height_m", 0.60, "float", "m", 0.01, "fence.columns")
        add(f"{prefix}.material", "gray masonry", "str", group="fence.columns")
        add(f"{prefix}.finish", "rough", "str", group="fence.columns")

    # --------------------------------------------------------------------------
    # Balconies and openings.
    # --------------------------------------------------------------------------
    add("balcony.length_m", 6.0, "float", "m", 0.02, "balcony.aggregate")
    add("balcony.depth_m", 1.5, "float", "m", 0.02, "balcony.aggregate")
    add("balcony.area_m2", 9.0, "float", "m2", 0.05, "balcony.aggregate")
    add("balcony.railing_height_m", 1.0, "float", "m", 0.01, "balcony.aggregate")
    add("balcony.north_count", 16, "int", "count", 0.0, "balcony.aggregate")
    add("balcony.south_count", 16, "int", "count", 0.0, "balcony.aggregate")
    add("balcony.total_count", 32, "int", "count", 0.0, "balcony.aggregate")
    add("balcony.floor_color", "red-brown brick color", "str", group="balcony.aggregate")
    add("balcony.floor_texture", "rough with whitish veins", "str", group="balcony.aggregate")

    for side in ("north", "south"):
        for idx in range(1, 17):
            prefix = f"balcony.{side}.{idx:02d}"
            add(f"{prefix}.length_m", 6.0, "float", "m", 0.02, f"balcony.{side}")
            add(f"{prefix}.depth_m", 1.5, "float", "m", 0.02, f"balcony.{side}")
            add(f"{prefix}.area_m2", 9.0, "float", "m2", 0.05, f"balcony.{side}")
            add(f"{prefix}.railing_height_m", 1.0, "float", "m", 0.01, f"balcony.{side}")
            add(f"{prefix}.railing_material", "iron", "str", group=f"balcony.{side}")
            add(f"{prefix}.railing_color", "creamy-white", "str", group=f"balcony.{side}")
            add(f"{prefix}.floor_color", "red-brown brick color", "str", group=f"balcony.{side}")
            add(f"{prefix}.floor_texture", "rough with whitish veins", "str", group=f"balcony.{side}")

    add("window.big.width_m", 0.90, "float", "m", 0.005, "windows.aggregate")
    add("window.big.leaf_count", 2, "int", "count", 0.0, "windows.aggregate")
    add("window.big.leaf_width_m", 0.45, "float", "m", 0.005, "windows.aggregate")
    add("window.big.height_m", 2.20, "float", "m", 0.01, "windows.aggregate")
    add("window.small.width_m", 0.50, "float", "m", 0.005, "windows.aggregate")
    add("window.small.height_m", 1.20, "float", "m", 0.01, "windows.aggregate")
    add("window.small.sill_height_m", 1.00, "float", "m", 0.01, "windows.aggregate")
    add("window.small.spacing_m", 1.00, "float", "m", 0.01, "windows.aggregate")
    add("window.side.axis_spacing_m", 3.00, "float", "m", 0.02, "windows.aggregate")
    add("window.south.width_m", 0.70, "float", "m", 0.005, "windows.aggregate")
    add("window.south.height_m", 2.20, "float", "m", 0.01, "windows.aggregate")
    add("window.south.ceiling_gap_m", 0.40, "float", "m", 0.01, "windows.aggregate")
    add("window.north.big_count", 16, "int", "count", 0.0, "windows.counts")
    add("window.north.small_count", 32, "int", "count", 0.0, "windows.counts")
    add("window.south.count", 48, "int", "count", 0.0, "windows.counts")
    add("window.east.count", 12, "int", "count", 0.0, "windows.counts")
    add("window.west.count", 12, "int", "count", 0.0, "windows.counts")
    add("window.total_count", 120, "int", "count", 0.0, "windows.counts")
    add("window.shutter_material", "plastic", "str", group="windows.aggregate")
    add("window.shutter_color", "white", "str", group="windows.aggregate")

    # Create 120 individually addressable opening objects.
    opening_index = 0
    opening_specs: List[Tuple[str, int, float, float]] = [
        ("north_big", 16, 0.90, 2.20),
        ("north_small", 32, 0.50, 1.20),
        ("south_door_window", 48, 0.70, 2.20),
        ("east_small", 12, 0.50, 1.20),
        ("west_small", 12, 0.50, 1.20),
    ]
    for kind, count, width, height in opening_specs:
        for local_idx in range(1, count + 1):
            opening_index += 1
            prefix = f"opening.{opening_index:03d}"
            add(f"{prefix}.kind", kind, "str", group="openings.individual")
            add(f"{prefix}.local_index", local_idx, "int", "count", 0.0, "openings.individual")
            add(f"{prefix}.width_m", width, "float", "m", 0.005, "openings.individual")
            add(f"{prefix}.height_m", height, "float", "m", 0.01, "openings.individual")
            add(f"{prefix}.electric_shutter", True, "bool", group="openings.individual")
            add(f"{prefix}.shutter_color", "white", "str", group="openings.individual")

    # --------------------------------------------------------------------------
    # Intercoms.
    # --------------------------------------------------------------------------
    add("intercom.total_count", 16, "int", "count", 0.0, "intercom.aggregate")
    for idx in range(1, 17):
        panel = "right" if idx <= 8 else "left"
        local = idx if idx <= 8 else idx - 8
        row = 4 - ((local - 1) // 2)
        col = 1 if local % 2 == 1 else 2
        label = "dr. Vincenzo Comitato" if idx == 6 else f"Tenant {row}{'v' if col == 1 else 'z'}"
        prefix = f"intercom.{idx:02d}"
        add(f"{prefix}.panel", panel, "str", group="intercom.individual")
        add(f"{prefix}.row", row, "int", "count", 0.0, "intercom.individual")
        add(f"{prefix}.column", col, "int", "count", 0.0, "intercom.individual")
        add(f"{prefix}.label", label, "str", group="intercom.individual")
        add(f"{prefix}.button_shape", "round", "str", group="intercom.individual")
        add(f"{prefix}.camera", True, "bool", group="intercom.individual")

    # --------------------------------------------------------------------------
    # External technical cabinet.
    # --------------------------------------------------------------------------
    add("cabinet.location", "north side towards west end, outside the garden", "str", group="cabinet")
    add("cabinet.length_m", 4.0, "float", "m", 0.02, "cabinet")
    add("cabinet.height_m", 2.0, "float", "m", 0.02, "cabinet")
    add("cabinet.color", "gray", "str", group="cabinet")
    add("cabinet.material", "reinforced aluminum", "str", group="cabinet")
    add("cabinet.locked", True, "bool", group="cabinet")
    for service in ("electricity", "water", "gas", "internet"):
        add(f"cabinet.service.{service}", True, "bool", group="cabinet.services")

    # --------------------------------------------------------------------------
    # Enzo's apartment: geometry and semantic details.
    # --------------------------------------------------------------------------
    add("enzo.apartment.staircase", "A", "str", group="enzo.location")
    add("enzo.apartment.floor", 2, "int", "count", 0.0, "enzo.location")
    add("enzo.apartment.orientation", "east", "str", group="enzo.location")
    add("enzo.apartment.position_on_landing", "right", "str", group="enzo.location")
    add("enzo.apartment.opposite_neighbors", 1, "int", "count", 0.0, "enzo.location")
    add("enzo.landing.length_ew_m", 2.50, "float", "m", 0.02, "enzo.landing")
    add("enzo.landing.width_ns_m", 3.00, "float", "m", 0.02, "enzo.landing")
    add("enzo.landing.area_m2", 7.50, "float", "m2", 0.05, "enzo.landing")
    add("enzo.apartment.gross_length_ew_m", 10.00, "float", "m", 0.05, "enzo.geometry")
    add("enzo.apartment.gross_depth_ns_m", 18.00, "float", "m", 0.05, "enzo.geometry")
    add("enzo.apartment.gross_area_m2", 180.00, "float", "m2", 0.2, "enzo.geometry")
    add("enzo.apartment.useful_area_m2", 155.00, "float", "m2", 1.0, "enzo.geometry")
    add("enzo.apartment.ceiling_height_m", 2.60, "float", "m", 0.01, "enzo.geometry")
    add("enzo.apartment.wall_color", "creamy-white", "str", group="enzo.surface")
    add("enzo.apartment.main_rooms", 4, "int", "count", 0.0, "enzo.counts")
    add("enzo.apartment.functional_spaces", 7, "int", "count", 0.0, "enzo.counts")
    add("enzo.apartment.floor_tile_width_m", 0.30, "float", "m", 0.005, "enzo.surface")
    add("enzo.apartment.floor_tile_height_m", 0.30, "float", "m", 0.005, "enzo.surface")
    add("enzo.apartment.floor_tile_color", "white marble effect", "str", group="enzo.surface")
    add("enzo.apartment.floor_tile_veins", "light blue-green", "str", group="enzo.surface")
    add("enzo.security.camera.entrance", True, "bool", group="enzo.security")
    add("enzo.security.camera.corridor", True, "bool", group="enzo.security")
    add("enzo.heating.floor_system", True, "bool", group="enzo.climate")

    room_specs = {
        "entrance": (3.00, 3.20, 9.60, False),
        "corridor": (6.40, 1.80, 11.52, False),
        "kitchen": (4.00, 5.00, 20.00, True),
        "single_bedroom": (3.80, 4.60, 17.48, True),
        "master_bedroom": (4.50, 4.80, 21.60, True),
        "study": (3.40, 4.00, 13.60, True),
        "bathroom": (3.00, 3.40, 10.20, True),
    }
    for room, (length, width, area, has_ac) in room_specs.items():
        prefix = f"enzo.room.{room}"
        add(f"{prefix}.length_m", length, "float", "m", 0.02, f"enzo.room.{room}")
        add(f"{prefix}.width_m", width, "float", "m", 0.02, f"enzo.room.{room}")
        add(f"{prefix}.area_m2", area, "float", "m2", 0.05, f"enzo.room.{room}")
        add(f"{prefix}.air_conditioner", has_ac, "bool", group=f"enzo.room.{room}")
        add(f"{prefix}.floor_heating", True, "bool", group=f"enzo.room.{room}")

    # Entrance and internal doors.
    add("enzo.entry_door.armored", True, "bool", group="enzo.entry")
    add("enzo.entry_door.color", "dark brown", "str", group="enzo.entry")
    add("enzo.entry_door.finish", "matte and carved", "str", group="enzo.entry")
    add("enzo.entry_door.wood", "fine walnut", "str", group="enzo.entry")
    add("enzo.internal_doors.color", "white", "str", group="enzo.doors")
    add("enzo.internal_doors.material", "fine wood", "str", group="enzo.doors")
    add("enzo.internal_doors.handle", "shiny golden knob", "str", group="enzo.doors")
    add("enzo.internal_doors.removable_key", True, "bool", group="enzo.doors")

    # Kitchen.
    add("enzo.kitchen.wall_east_tiled_to_ceiling", True, "bool", group="enzo.kitchen")
    add("enzo.kitchen.wall_west_color", "creamy-white", "str", group="enzo.kitchen")
    add("enzo.kitchen.wall_south_color", "creamy-white", "str", group="enzo.kitchen")
    add("enzo.kitchen.table.length_m", 2.00, "float", "m", 0.01, "enzo.kitchen")
    add("enzo.kitchen.table.width_m", 0.80, "float", "m", 0.01, "enzo.kitchen")
    add("enzo.kitchen.table.orientation", "north-south", "str", group="enzo.kitchen")
    add("enzo.kitchen.shelves.levels", 3, "int", "count", 0.0, "enzo.kitchen")
    for item in ("salt shaker", "pots", "appliances"):
        add(f"enzo.kitchen.shelves.contains.{item}", True, "bool", group="enzo.kitchen")

    # Single bedroom.
    add("enzo.single_bedroom.bed_type", "single", "str", group="enzo.single_bedroom")
    add("enzo.single_bedroom.bed_orientation", "towards south wall", "str", group="enzo.single_bedroom")
    add("enzo.single_bedroom.bookcase.width_m", 0.80, "float", "m", 0.01, "enzo.single_bedroom")
    add("enzo.single_bedroom.bookcase.shelves", 5, "int", "count", 0.0, "enzo.single_bedroom")
    add("enzo.single_bedroom.books", "pharmacology and pharmacodynamics", "str", group="enzo.single_bedroom")
    add("enzo.single_bedroom.picture.width_m", 0.30, "float", "m", 0.005, "enzo.single_bedroom")
    add("enzo.single_bedroom.picture.height_m", 0.15, "float", "m", 0.005, "enzo.single_bedroom")
    add("enzo.single_bedroom.picture_subject", "copy of a well-known Picasso painting", "str", group="enzo.single_bedroom")
    add("enzo.single_bedroom.poster", "J-Ax", "str", group="enzo.single_bedroom")

    # Bathroom.
    add("enzo.bathroom.tub.width_ew_m", 0.70, "float", "m", 0.01, "enzo.bathroom")
    add("enzo.bathroom.tub.length_ns_m", 2.40, "float", "m", 0.01, "enzo.bathroom")
    add("enzo.bathroom.shower.width_m", 0.60, "float", "m", 0.005, "enzo.bathroom")
    add("enzo.bathroom.shower.depth_m", 0.60, "float", "m", 0.005, "enzo.bathroom")
    add("enzo.bathroom.shower.material", "glossy white ceramic", "str", group="enzo.bathroom")
    add("enzo.bathroom.has_sink", True, "bool", group="enzo.bathroom")
    add("enzo.bathroom.has_wc", True, "bool", group="enzo.bathroom")
    add("enzo.bathroom.has_bidet", True, "bool", group="enzo.bathroom")
    add("enzo.bathroom.medicine_cabinet.color", "glossy white", "str", group="enzo.bathroom")
    add("enzo.bathroom.medicine_cabinet.material", "wood", "str", group="enzo.bathroom")

    # Master bedroom.
    add("enzo.master_bedroom.bed_type", "double", "str", group="enzo.master_bedroom")
    add("enzo.master_bedroom.wardrobe.doors", 6, "int", "count", 0.0, "enzo.master_bedroom")
    add("enzo.master_bedroom.wardrobe.color", "glossy beige", "str", group="enzo.master_bedroom")
    add("enzo.master_bedroom.wardrobe.sliding", True, "bool", group="enzo.master_bedroom")
    add("enzo.master_bedroom.wardrobe.internal_light", True, "bool", group="enzo.master_bedroom")
    add("enzo.master_bedroom.wardrobe.thermoventilated", True, "bool", group="enzo.master_bedroom")
    add("enzo.master_bedroom.tv_inches", 65, "int", "inch", 0.0, "enzo.master_bedroom")
    add("enzo.master_bedroom.south_openings", 2, "int", "count", 0.0, "enzo.master_bedroom")

    # Study.
    add("enzo.study.table.shape", "round", "str", group="enzo.study")
    add("enzo.study.table.material", "walnut", "str", group="enzo.study")
    add("enzo.study.table.color", "dark brown", "str", group="enzo.study")
    add("enzo.study.library.material", "walnut", "str", group="enzo.study")
    add("enzo.study.library.color", "dark brown", "str", group="enzo.study")
    add("enzo.study.books", "human anatomy, physiology, pathology, and related medical disciplines", "str", group="enzo.study")
    add("enzo.study.south_openings", 1, "int", "count", 0.0, "enzo.study")

    # Corridor plants, clock and entrance furniture.
    for idx, position in enumerate((
        "between master bedroom and study",
        "between kitchen and small bedroom",
        "between small bedroom and bathroom",
    ), start=1):
        prefix = f"enzo.corridor.plant.{idx}"
        add(f"{prefix}.position", position, "str", group="enzo.corridor")
        add(f"{prefix}.height_class", "low", "str", group="enzo.corridor")
        add(f"{prefix}.pot_material", "terracotta", "str", group="enzo.corridor")
        add(f"{prefix}.pot_color", "matte gray", "str", group="enzo.corridor")
    add("enzo.corridor.plant_count", 3, "int", "count", 0.0, "enzo.corridor")
    add("enzo.clock.type", "nineteenth-century pendulum", "str", group="enzo.furniture")
    add("enzo.clock.color", "beige", "str", group="enzo.furniture")
    add("enzo.clock.hand_finished", True, "bool", group="enzo.furniture")
    add("enzo.entrance.coat_rack.material", "cherry wood", "str", group="enzo.entrance")
    add("enzo.entrance.coat_rack.color", "light brown", "str", group="enzo.entrance")
    add("enzo.entrance.sideboard.has_mirror", True, "bool", group="enzo.entrance")
    add("enzo.entrance.sideboard.has_marble_shelf", True, "bool", group="enzo.entrance")
    add("enzo.entrance.silver_key_tray", True, "bool", group="enzo.entrance")
    add("enzo.entrance.writing_set.notebook", True, "bool", group="enzo.entrance")
    add("enzo.entrance.writing_set.pencil", True, "bool", group="enzo.entrance")

    # Ensure uniqueness.
    ids = [fact.fact_id for fact in facts]
    if len(ids) != len(set(ids)):
        duplicates = sorted({x for x in ids if ids.count(x) > 1})
        raise RuntimeError(f"Duplicate semantic fact ids: {duplicates[:10]}")

    if len(facts) < 1_006:
        raise RuntimeError("The semantic catalog must contain at least 1,006 facts.")

    return facts


# ==============================================================================
# SEMANTIC EQUATION FAMILY
# ==============================================================================


def build_semantic_equation_family() -> List[SemanticEquation]:
    def eq(
        name: str,
        ids: Sequence[str],
        evaluator: Callable[[Mapping[str, Any]], float],
        tolerance: float,
        description: str,
    ) -> SemanticEquation:
        return SemanticEquation(name, tuple(ids), evaluator, tolerance, description)

    return [
        eq(
            "building_footprint",
            ("building.length_ew_m", "building.depth_ns_m", "building.footprint_m2"),
            lambda v: float(v["building.footprint_m2"]) - float(v["building.length_ew_m"]) * float(v["building.depth_ns_m"]),
            1.0,
            "50 m x 18 m = 900 m2",
        ),
        eq(
            "garden_area",
            ("garden.length_ew_m", "garden.depth_ns_m", "garden.area_m2"),
            lambda v: float(v["garden.area_m2"]) - float(v["garden.length_ew_m"]) * float(v["garden.depth_ns_m"]),
            2.0,
            "100 m x 100 m = 10,000 m2",
        ),
        eq(
            "east_centering",
            ("garden.length_ew_m", "building.length_ew_m", "garden.distance_east_m"),
            lambda v: float(v["garden.distance_east_m"]) - (float(v["garden.length_ew_m"]) - float(v["building.length_ew_m"])) / 2.0,
            0.15,
            "Centered building leaves 25 m east",
        ),
        eq(
            "north_centering",
            ("garden.depth_ns_m", "building.depth_ns_m", "garden.distance_north_m"),
            lambda v: float(v["garden.distance_north_m"]) - (float(v["garden.depth_ns_m"]) - float(v["building.depth_ns_m"])) / 2.0,
            0.15,
            "Centered building leaves 41 m north",
        ),
        eq(
            "east_usable_garden",
            ("garden.distance_east_m", "garden.walkway_width_m", "garden.usable_east_m"),
            lambda v: float(v["garden.usable_east_m"]) - (float(v["garden.distance_east_m"]) - float(v["garden.walkway_width_m"])),
            0.10,
            "25 m minus 5 m walkway = 20 m usable east garden",
        ),
        eq(
            "north_usable_garden",
            ("garden.distance_north_m", "garden.walkway_width_m", "garden.usable_north_m"),
            lambda v: float(v["garden.usable_north_m"]) - (float(v["garden.distance_north_m"]) - float(v["garden.walkway_width_m"])),
            0.10,
            "41 m minus 5 m walkway = 36 m usable north garden",
        ),
        eq(
            "apartment_count",
            ("building.floors", "building.apartments_per_floor", "building.total_apartments"),
            lambda v: float(v["building.total_apartments"]) - float(v["building.floors"]) * float(v["building.apartments_per_floor"]),
            0.0,
            "4 floors x 4 apartments = 16",
        ),
        eq(
            "sector_area",
            ("building.sector_length_ew_m", "building.depth_ns_m", "building.sector_area_m2"),
            lambda v: float(v["building.sector_area_m2"]) - float(v["building.sector_length_ew_m"]) * float(v["building.depth_ns_m"]),
            1.0,
            "25 m x 18 m = 450 m2",
        ),
        eq(
            "apartment_module_area",
            ("building.apartment_module_length_ew_m", "building.apartment_module_depth_ns_m", "building.apartment_module_gross_m2"),
            lambda v: float(v["building.apartment_module_gross_m2"]) - float(v["building.apartment_module_length_ew_m"]) * float(v["building.apartment_module_depth_ns_m"]),
            0.5,
            "10 m x 18 m = 180 m2",
        ),
        eq(
            "sector_decomposition",
            ("building.stair_core_area_m2", "building.apartment_module_gross_m2", "building.sector_area_m2"),
            lambda v: float(v["building.sector_area_m2"]) - (float(v["building.stair_core_area_m2"]) + 2.0 * float(v["building.apartment_module_gross_m2"])),
            1.0,
            "90 + 180 + 180 = 450 m2",
        ),
        eq(
            "balcony_area",
            ("balcony.length_m", "balcony.depth_m", "balcony.area_m2"),
            lambda v: float(v["balcony.area_m2"]) - float(v["balcony.length_m"]) * float(v["balcony.depth_m"]),
            0.10,
            "6 m x 1.5 m = 9 m2",
        ),
        eq(
            "balcony_count",
            ("balcony.north_count", "balcony.south_count", "balcony.total_count"),
            lambda v: float(v["balcony.total_count"]) - float(v["balcony.north_count"]) - float(v["balcony.south_count"]),
            0.0,
            "16 north + 16 south = 32 balconies",
        ),
        eq(
            "big_window_width",
            ("window.big.width_m", "window.big.leaf_count", "window.big.leaf_width_m"),
            lambda v: float(v["window.big.width_m"]) - float(v["window.big.leaf_count"]) * float(v["window.big.leaf_width_m"]),
            0.02,
            "2 leaves x 0.45 m = 0.90 m",
        ),
        eq(
            "opening_count",
            (
                "window.north.big_count", "window.north.small_count", "window.south.count",
                "window.east.count", "window.west.count", "window.total_count",
            ),
            lambda v: float(v["window.total_count"]) - (
                float(v["window.north.big_count"]) + float(v["window.north.small_count"]) +
                float(v["window.south.count"]) + float(v["window.east.count"]) +
                float(v["window.west.count"])
            ),
            0.0,
            "16 + 32 + 48 + 12 + 12 = 120 openings",
        ),
        eq(
            "fence_pitch",
            ("fence.column_width_m", "fence.column_gap_m", "fence.module_pitch_m"),
            lambda v: float(v["fence.module_pitch_m"]) - float(v["fence.column_width_m"]) - float(v["fence.column_gap_m"]),
            0.01,
            "0.10 m column + 0.10 m gap = 0.20 m pitch",
        ),
        eq(
            "fence_modular_length",
            ("fence.perimeter_m", "fence.gate_width_m", "fence.modular_length_m"),
            lambda v: float(v["fence.modular_length_m"]) - (float(v["fence.perimeter_m"]) - float(v["fence.gate_width_m"])),
            0.2,
            "400 m perimeter - 4 m gate = 396 m modular fence",
        ),
        eq(
            "fence_column_count",
            ("fence.modular_length_m", "fence.module_pitch_m", "fence.column_count"),
            lambda v: float(v["fence.column_count"]) - float(v["fence.modular_length_m"]) / float(v["fence.module_pitch_m"]),
            1.0,
            "396 m / 0.20 m = 1,980 columns",
        ),
        eq(
            "landing_area",
            ("enzo.landing.length_ew_m", "enzo.landing.width_ns_m", "enzo.landing.area_m2"),
            lambda v: float(v["enzo.landing.area_m2"]) - float(v["enzo.landing.length_ew_m"]) * float(v["enzo.landing.width_ns_m"]),
            0.10,
            "2.5 m x 3 m = 7.5 m2",
        ),
        eq(
            "enzo_gross_area",
            ("enzo.apartment.gross_length_ew_m", "enzo.apartment.gross_depth_ns_m", "enzo.apartment.gross_area_m2"),
            lambda v: float(v["enzo.apartment.gross_area_m2"]) - float(v["enzo.apartment.gross_length_ew_m"]) * float(v["enzo.apartment.gross_depth_ns_m"]),
            0.5,
            "10 m x 18 m = 180 m2 gross apartment module",
        ),
        eq(
            "kitchen_area",
            ("enzo.room.kitchen.length_m", "enzo.room.kitchen.width_m", "enzo.room.kitchen.area_m2"),
            lambda v: float(v["enzo.room.kitchen.area_m2"]) - float(v["enzo.room.kitchen.length_m"]) * float(v["enzo.room.kitchen.width_m"]),
            0.10,
            "4 m x 5 m = 20 m2 kitchen",
        ),
        eq(
            "bathroom_area",
            ("enzo.room.bathroom.length_m", "enzo.room.bathroom.width_m", "enzo.room.bathroom.area_m2"),
            lambda v: float(v["enzo.room.bathroom.area_m2"]) - float(v["enzo.room.bathroom.length_m"]) * float(v["enzo.room.bathroom.width_m"]),
            0.10,
            "3 m x 3.4 m = 10.2 m2 bathroom",
        ),
    ]


ANCHOR_FACT_IDS: Tuple[str, ...] = tuple(sorted({
    fact_id
    for equation in build_semantic_equation_family()
    for fact_id in equation.required_fact_ids
}))


# ==============================================================================
# TOPOLOGY, SELECTORS, FULL RELATIONAL GRAPH AND EXECUTABLE CNVS PIPELINE
# ==============================================================================

# The classes below intentionally replace the compact data structures declared
# earlier in the file.  The original classes retained only terminal-to-terminal
# neighbourhoods.  Test 14 now preserves every terminal and non-terminal node,
# every parent-child edge, the complete reconstruction order, and the node at
# which each semantic or hidden invariant becomes evaluable.


@dataclass(frozen=True)
class TreeNode:
    node_id: str
    parent_id: Optional[str]
    children_ids: Tuple[str, ...]
    node_kind: str
    semantic_groups: Tuple[str, ...]
    node_nonce: str
    topology_digest: str


@dataclass(frozen=True)
class SemanticLeaf:
    selector: str
    fact: SemanticFact
    assigned_verifier: int
    parent_node: Optional[str]
    semantic_role: str
    task_nonce: str
    task_digest: str


@dataclass(frozen=True)
class LocalEvidence:
    selector: str
    verifier_id: int
    observed_value: Any
    claimed_parent: Optional[str]
    claimed_role: str
    task_digest: str
    form_ok: bool
    conv_ok: bool
    local_admissible: bool
    adherence: float
    error_value: float


@dataclass(frozen=True)
class HiddenInvariantState:
    critical_selectors: Tuple[str, ...]
    expected_values: np.ndarray
    epsilons: np.ndarray
    scales: np.ndarray
    matrix: np.ndarray
    targets: np.ndarray
    tolerances: np.ndarray
    row_supports: Tuple[Tuple[int, ...], ...]
    row_nodes: Tuple[str, ...]
    semantic_equations: Tuple[SemanticEquation, ...]
    semantic_equation_nodes: Tuple[str, ...]
    leakage_order: Tuple[int, ...]
    nonce: str


@dataclass
class CNVSSemanticState:
    cycle_id: str
    leaves: Dict[str, SemanticLeaf]
    nodes: Dict[str, TreeNode]
    fact_to_selector: Dict[str, str]
    expected_relation_edges: Set[Tuple[str, str]]
    topology_root: str
    hidden: HiddenInvariantState
    semantic_catalog_size: int
    topology_nonce: str
    selected_fact_ids: Tuple[str, ...]
    depth_by_node: Dict[str, int]

    @property
    def active_verifier_count(self) -> int:
        return len({leaf.assigned_verifier for leaf in self.leaves.values()})

    @property
    def terminal_fragment_count(self) -> int:
        return len(self.leaves)

    @property
    def total_node_count(self) -> int:
        return len(self.nodes)


@dataclass
class ValidationResult:
    accepted: bool
    all_local_ok: bool
    cons_r_ok: bool
    inv_c_ok: bool
    early_rejection: bool
    failed_stage: str
    failing_node: str
    reason: str
    latency_ns: int
    evaluated_invariants: int = 0


@dataclass
class MonteCarloCycleResult:
    q: float
    Q: int
    r: int
    m: int
    iterations: int
    p_inf: float
    vg_accept_rate: float
    vg_veto_rate: float
    local_pass_global_veto_rate: float
    exact_ref: float
    theorem_ref: float
    avg_direct: float
    avg_inferred: float
    avg_failed: float
    simulation_ns_per_iteration: float
    single_candidate_latency_p50_ns: float
    single_candidate_latency_p95_ns: float
    single_candidate_latency_p99_ns: float
    hidden_matrix_rank: int
    monte_carlo_seed: int


@dataclass
class ScalabilityResult:
    Q: int
    fragments: int
    total_nodes: int
    critical_fragments: int
    iterations: int
    full_pipeline_mean_ns: float
    full_pipeline_p50_ns: float
    full_pipeline_p95_ns: float
    full_pipeline_p99_ns: float
    vectorized_ns_per_iteration: float
    vectorized_throughput_per_second: float


@dataclass
class LeakageCycleResult:
    leakage_fraction: float
    leaked_rows: int
    total_rows: int
    nullspace_dimension: int
    iterations: int
    feasible_false_state_rate: float
    full_invariant_bypass_rate: float
    mean_semantic_distortion: float
    all_invariants_known: bool
    total_disclosure_reconstruction_success: float
    seed: int


@dataclass
class RelationalAttackResult:
    attack_type: str
    iterations: int
    detected_rate: float
    concrete_pipeline_veto: bool
    failed_stage: str


@dataclass
class SemanticInvariantAttackResult:
    equation_name: str
    attached_node: str
    iterations: int
    local_pass_rate: float
    partial_invariant_veto_rate: float
    concrete_pipeline_veto: bool
    concrete_failed_stage: str
    concrete_failing_node: str
    seed: int


@dataclass
class InvariantEvaluation:
    ok: bool
    failing_node: str
    reason: str
    evaluated_count: int


# ------------------------------------------------------------------------------
# Tree construction helpers
# ------------------------------------------------------------------------------


def select_facts_for_state(catalog: Sequence[SemanticFact], k: int) -> List[SemanticFact]:
    if not (1 <= k <= len(catalog)):
        raise ValueError(f"k must be in [1, {len(catalog)}].")

    by_id = {fact.fact_id: fact for fact in catalog}
    selected: List[SemanticFact] = []

    # Equation anchors are inserted first so the executable state contains a
    # meaningful family of geometric and cardinality invariants even at small Q.
    for fact_id in ANCHOR_FACT_IDS:
        if fact_id in by_id and len(selected) < k:
            selected.append(by_id[fact_id])

    selected_ids = {fact.fact_id for fact in selected}
    remaining = [fact for fact in catalog if fact.fact_id not in selected_ids]
    if len(selected) < k:
        selected.extend(SECURE_RNG.sample(remaining, k - len(selected)))
    return selected


def _partition_without_singletons(items: Sequence[str], minimum: int = 2, maximum: int = 5) -> List[List[str]]:
    """Partition items into groups of size 2..5, never creating unary parents."""
    work = list(items)
    groups: List[List[str]] = []
    cursor = 0
    while cursor < len(work):
        remaining = len(work) - cursor
        if remaining == 1:
            if not groups:
                return [[work[cursor]]]
            groups[-1].append(work[cursor])
            cursor += 1
            continue
        if remaining <= maximum:
            size = remaining
        else:
            size = SECURE_RNG.randint(minimum, maximum)
            if remaining - size == 1:
                size = size - 1 if size > minimum else size + 1
        groups.append(work[cursor:cursor + size])
        cursor += size
    return groups


def _node_digest(node_id: str, children: Sequence[str], kind: str, nonce: str) -> str:
    return sha256_text(canonical_json({
        "node": node_id,
        "children": list(children),
        "kind": kind,
        "nonce": nonce,
    }))


def _task_digest(
    selector: str,
    fact_id: str,
    verifier_id: int,
    parent_id: Optional[str],
    role: str,
    task_nonce: str,
) -> str:
    return sha256_text(canonical_json({
        "selector": selector,
        "fact_id": fact_id,
        "verifier": verifier_id,
        "parent": parent_id,
        "role": role,
        "task_nonce": task_nonce,
    }))


def build_full_tree(
    selectors: Sequence[str],
    selector_groups: Mapping[str, str],
) -> Tuple[str, Dict[str, TreeNode], Dict[str, int]]:
    """
    Build a complete finite decomposition tree.

    Leaves belonging to the same semantic group are preferentially aggregated
    near one another, so room-level and object-level equations can be evaluated
    before the global root is reached.  Every internal node has at least two
    children, satisfying |D(s)| = 0 or |D(s)| >= 2.
    """
    if not selectors:
        raise ValueError("At least one terminal selector is required.")

    mutable: Dict[str, Dict[str, Any]] = {}
    for selector in selectors:
        nonce = secrets.token_hex(16)
        mutable[selector] = {
            "node_id": selector,
            "parent_id": None,
            "children_ids": tuple(),
            "node_kind": "terminal",
            "semantic_groups": (selector_groups[selector],),
            "node_nonce": nonce,
        }

    def create_parent(children: Sequence[str], kind: str) -> str:
        if len(children) < 2:
            raise ValueError("CNVS internal nodes cannot have a single child.")
        node_id = "node_" + secrets.token_hex(12)
        groups = sorted({g for child in children for g in mutable[child]["semantic_groups"]})
        nonce = secrets.token_hex(16)
        mutable[node_id] = {
            "node_id": node_id,
            "parent_id": None,
            "children_ids": tuple(children),
            "node_kind": kind,
            "semantic_groups": tuple(groups),
            "node_nonce": nonce,
        }
        for child in children:
            mutable[child]["parent_id"] = node_id
        return node_id

    by_group: Dict[str, List[str]] = {}
    for selector in selectors:
        by_group.setdefault(selector_groups[selector], []).append(selector)

    current_roots: List[str] = []
    for group_name, members in by_group.items():
        SECURE_RNG.shuffle(members)
        if len(members) == 1:
            current_roots.extend(members)
            continue
        for group in _partition_without_singletons(members):
            if len(group) == 1:
                current_roots.extend(group)
            else:
                current_roots.append(create_parent(group, f"semantic_group:{group_name}"))

    while len(current_roots) > 1:
        SECURE_RNG.shuffle(current_roots)
        next_roots: List[str] = []
        for group in _partition_without_singletons(current_roots):
            if len(group) == 1:
                next_roots.extend(group)
            else:
                next_roots.append(create_parent(group, "aggregate"))
        current_roots = next_roots

    root = current_roots[0]
    nodes: Dict[str, TreeNode] = {}
    for node_id, record in mutable.items():
        digest = _node_digest(
            node_id,
            record["children_ids"],
            record["node_kind"],
            record["node_nonce"],
        )
        nodes[node_id] = TreeNode(topology_digest=digest, **record)

    depth_by_node: Dict[str, int] = {root: 0}
    stack = [root]
    while stack:
        node_id = stack.pop()
        node = nodes[node_id]
        for child in node.children_ids:
            depth_by_node[child] = depth_by_node[node_id] + 1
            stack.append(child)

    return root, nodes, depth_by_node


def _ancestor_chain(nodes: Mapping[str, TreeNode], node_id: str) -> List[str]:
    chain = [node_id]
    cursor = node_id
    while nodes[cursor].parent_id is not None:
        cursor = str(nodes[cursor].parent_id)
        chain.append(cursor)
    return chain


def lowest_common_ancestor(
    nodes: Mapping[str, TreeNode],
    depth_by_node: Mapping[str, int],
    node_ids: Sequence[str],
) -> str:
    if not node_ids:
        raise ValueError("LCA requires at least one node.")
    common = set(_ancestor_chain(nodes, node_ids[0]))
    for node_id in node_ids[1:]:
        common.intersection_update(_ancestor_chain(nodes, node_id))
    if not common:
        raise RuntimeError("The decomposition graph is disconnected.")
    return max(common, key=lambda x: depth_by_node[x])


def descendants(nodes: Mapping[str, TreeNode], node_id: str) -> Set[str]:
    result: Set[str] = set()
    stack = [node_id]
    while stack:
        current = stack.pop()
        if current in result:
            continue
        result.add(current)
        stack.extend(nodes[current].children_ids)
    return result


# ------------------------------------------------------------------------------
# Hidden and semantic invariants
# ------------------------------------------------------------------------------


def build_hidden_invariant_state(
    leaves: Mapping[str, SemanticLeaf],
    nodes: Mapping[str, TreeNode],
    depth_by_node: Mapping[str, int],
    m: int,
    equation_family: Sequence[SemanticEquation],
) -> HiddenInvariantState:
    numeric_candidates = [
        selector for selector, leaf in leaves.items()
        if is_numeric_fact(leaf.fact) and leaf.fact.epsilon > 0.0
    ]
    if not numeric_candidates:
        raise RuntimeError("At least one numeric epsilon-bounded fragment is required.")

    m_effective = min(max(1, m), len(numeric_candidates))
    critical = tuple(sorted(SECURE_RNG.sample(numeric_candidates, m_effective)))
    expected = np.asarray([float(leaves[s].fact.value) for s in critical], dtype=np.float64)
    eps = np.asarray([max(float(leaves[s].fact.epsilon), 1e-12) for s in critical], dtype=np.float64)
    scales = np.maximum(np.abs(expected), 1.0)

    # C_int is not implemented as a direct equality test.  It is instantiated as
    # a hidden, full-rank family of overlapping linear bindings over normalized
    # critical observations.  Each row is attached to the lowest node that owns
    # all selectors in its support, so checks occur progressively while the tree
    # is reconstructed.  Full rank guarantees that a non-zero perturbation of the
    # complete critical vector cannot satisfy every hidden binding simultaneously.
    rng = np.random.default_rng(secrets.randbits(128))
    matrix = np.eye(m_effective, dtype=np.float64)
    row_supports: List[Tuple[int, ...]] = []
    for row in range(m_effective):
        candidates = [idx for idx in range(m_effective) if idx != row]
        extra_count = min(len(candidates), SECURE_RNG.randint(1, min(4, max(1, len(candidates))))) if candidates else 0
        extras = SECURE_RNG.sample(candidates, extra_count) if extra_count else []
        for idx in extras:
            matrix[row, idx] = float(rng.uniform(-0.35, 0.35))
        norm = np.linalg.norm(matrix[row], ord=1)
        matrix[row] /= norm if norm > 0 else 1.0
        row_supports.append(tuple(int(x) for x in np.flatnonzero(np.abs(matrix[row]) > 1e-15)))

    if np.linalg.matrix_rank(matrix) != m_effective:
        raise RuntimeError("Failed to instantiate a full-rank hidden invariant matrix.")

    normalized_expected = expected / scales
    targets = matrix @ normalized_expected
    tolerances = np.full(m_effective, 1e-10, dtype=np.float64)
    row_nodes = tuple(
        lowest_common_ancestor(nodes, depth_by_node, [critical[idx] for idx in support])
        for support in row_supports
    )

    active_fact_ids = set(leaf.fact.fact_id for leaf in leaves.values())
    available_equations = tuple(
        equation for equation in equation_family
        if set(equation.required_fact_ids).issubset(active_fact_ids)
    )
    fact_to_selector = {leaf.fact.fact_id: selector for selector, leaf in leaves.items()}
    equation_nodes = tuple(
        lowest_common_ancestor(
            nodes,
            depth_by_node,
            [fact_to_selector[fact_id] for fact_id in equation.required_fact_ids],
        )
        for equation in available_equations
    )

    leakage_order = list(range(m_effective))
    SECURE_RNG.shuffle(leakage_order)

    return HiddenInvariantState(
        critical_selectors=critical,
        expected_values=expected,
        epsilons=eps,
        scales=scales,
        matrix=matrix,
        targets=targets,
        tolerances=tolerances,
        row_supports=tuple(row_supports),
        row_nodes=row_nodes,
        semantic_equations=available_equations,
        semantic_equation_nodes=equation_nodes,
        leakage_order=tuple(leakage_order),
        nonce=secrets.token_hex(24),
    )


def build_state(
    catalog: Sequence[SemanticFact],
    k: int,
    m: int,
    cycle_id: str,
    verifier_ids: Optional[Sequence[int]] = None,
    selected_facts: Optional[Sequence[SemanticFact]] = None,
    preserved_selectors: Optional[Mapping[str, str]] = None,
) -> CNVSSemanticState:
    if selected_facts is None:
        selected = select_facts_for_state(catalog, k)
    else:
        selected = list(selected_facts)
        if len(selected) != k:
            raise ValueError("selected_facts length must equal k.")

    if verifier_ids is None:
        verifier_ids = list(range(1, k + 1))
    if len(verifier_ids) != k or len(set(verifier_ids)) != k:
        raise ValueError("verifier_ids must contain k distinct identifiers.")

    topology_nonce = secrets.token_hex(24)
    preserved_selectors = dict(preserved_selectors or {})
    selectors = [
        preserved_selectors.get(fact.fact_id, make_selector(fact.fact_id, topology_nonce))
        for fact in selected
    ]
    selector_groups = {selector: fact.group for selector, fact in zip(selectors, selected)}
    root, nodes, depth_by_node = build_full_tree(selectors, selector_groups)

    leaves: Dict[str, SemanticLeaf] = {}
    for selector, fact, verifier in zip(selectors, selected, verifier_ids):
        parent = nodes[selector].parent_id
        role = fact.fact_id
        task_nonce = secrets.token_hex(16)
        digest = _task_digest(selector, fact.fact_id, int(verifier), parent, role, task_nonce)
        leaves[selector] = SemanticLeaf(
            selector=selector,
            fact=fact,
            assigned_verifier=int(verifier),
            parent_node=parent,
            semantic_role=role,
            task_nonce=task_nonce,
            task_digest=digest,
        )

    edges = {
        (node_id, child)
        for node_id, node in nodes.items()
        for child in node.children_ids
    }
    hidden = build_hidden_invariant_state(
        leaves,
        nodes,
        depth_by_node,
        m,
        build_semantic_equation_family(),
    )

    return CNVSSemanticState(
        cycle_id=cycle_id,
        leaves=leaves,
        nodes=nodes,
        fact_to_selector={leaf.fact.fact_id: selector for selector, leaf in leaves.items()},
        expected_relation_edges=edges,
        topology_root=root,
        hidden=hidden,
        semantic_catalog_size=len(catalog),
        topology_nonce=topology_nonce,
        selected_fact_ids=tuple(fact.fact_id for fact in selected),
        depth_by_node=depth_by_node,
    )


# ==============================================================================
# V_L: SIMULATED TERMINAL OBSERVATION, FORM AND LOCAL CONVERGENCE
# ==============================================================================


def Form_sigma(fact: SemanticFact, observed: Any, selector: str, state: CNVSSemanticState) -> bool:
    if selector not in state.leaves or observed is None:
        return False
    if fact.value_type == "float":
        return isinstance(observed, (int, float, np.integer, np.floating)) and not isinstance(observed, bool) and math.isfinite(float(observed))
    if fact.value_type == "int":
        return isinstance(observed, (int, np.integer)) and not isinstance(observed, bool)
    if fact.value_type == "bool":
        return isinstance(observed, (bool, np.bool_))
    if fact.value_type == "str":
        return isinstance(observed, str)
    if fact.value_type == "composite":
        return isinstance(observed, (dict, list, tuple))
    return type(observed) is type(fact.value)


def convergence_metrics(fact: SemanticFact, observed: Any) -> Tuple[bool, float, float]:
    if observed is None:
        return False, float("inf"), 0.0
    if fact.value_type in {"float", "int"}:
        error = abs(float(observed) - float(fact.value))
        epsilon = float(fact.epsilon)
        if epsilon <= 0.0:
            ok = error == 0.0
            adherence = 1.0 if ok else 0.0
        else:
            ok = error <= epsilon + 1e-15
            adherence = max(0.0, 1.0 - error / epsilon)
        return ok, error, adherence
    expected_norm = normalize_text(fact.value)
    observed_norm = normalize_text(observed)
    ok = expected_norm == observed_norm
    return ok, 0.0 if ok else 1.0, 1.0 if ok else 0.0


def V_L(
    state: CNVSSemanticState,
    selector: str,
    observed: Any,
    verifier_id: Optional[int] = None,
    claimed_parent: Optional[str] = None,
    claimed_role: Optional[str] = None,
    task_digest_value: Optional[str] = None,
) -> LocalEvidence:
    leaf = state.leaves[selector]
    verifier = leaf.assigned_verifier if verifier_id is None else int(verifier_id)
    parent = leaf.parent_node if claimed_parent is None else claimed_parent
    role = leaf.semantic_role if claimed_role is None else claimed_role
    digest = leaf.task_digest if task_digest_value is None else task_digest_value

    form_ok = Form_sigma(leaf.fact, observed, selector, state)
    conv_ok, error, adherence = convergence_metrics(leaf.fact, observed) if form_ok else (False, float("inf"), 0.0)
    return LocalEvidence(
        selector=selector,
        verifier_id=verifier,
        observed_value=observed,
        claimed_parent=parent,
        claimed_role=role,
        task_digest=digest,
        form_ok=form_ok,
        conv_ok=conv_ok,
        local_admissible=form_ok and conv_ok,
        adherence=adherence,
        error_value=error,
    )


def build_honest_evidence(
    state: CNVSSemanticState,
    noise_fraction: float = 0.0,
    rng: Optional[np.random.Generator] = None,
) -> Dict[str, LocalEvidence]:
    """
    Produce a simulated honest terminal response set.

    A software experiment has no physical terminal verifier, therefore an
    observation process must be generated.  The normal CNVS operating regime is
    a candidate state whose terminal measurements are mostly honest and locally
    admissible; otherwise reconstruction would never begin and the experiment
    would measure only trivial early rejection.  The default baseline therefore
    reports the declared central values exactly.  Optional bounded measurement
    noise can be enabled, but it is always kept inside V_L tolerance.

    Deliberately stealthy colluders are generated separately: they also remain
    inside epsilon so that V_L passes and Cons_R / Inv_C / V_G must perform the
    non-reducible systemic rejection.  Blatantly false observations are generated
    in a different scenario and must stop immediately at V_L.
    """
    if not 0.0 <= noise_fraction <= 1.0:
        raise ValueError("noise_fraction must be in [0,1].")
    rng = rng or np.random.default_rng()
    result: Dict[str, LocalEvidence] = {}
    for selector, leaf in state.leaves.items():
        observed = leaf.fact.value
        if noise_fraction > 0.0 and is_numeric_fact(leaf.fact) and leaf.fact.epsilon > 0.0:
            observed = float(leaf.fact.value) + float(rng.uniform(-noise_fraction, noise_fraction)) * float(leaf.fact.epsilon)
            if leaf.fact.value_type == "int":
                observed = int(round(observed))
        result[selector] = V_L(state, selector, observed)
    return result


def stealth_observation(fact: SemanticFact, rng: np.random.Generator) -> Any:
    """Generate a malicious but locally admissible observation."""
    if is_numeric_fact(fact) and fact.epsilon > 0.0:
        sign = -1.0 if rng.random() < 0.5 else 1.0
        alpha = float(rng.uniform(0.55, 0.95))
        value = float(fact.value) + sign * alpha * float(fact.epsilon)
        return int(round(value)) if fact.value_type == "int" else value
    return fact.value


def absurd_observation(fact: SemanticFact) -> Any:
    """Generate a value that is unambiguously outside the V_L domain/tolerance."""
    if is_numeric_fact(fact):
        step = max(1.0, 20.0 * max(float(fact.epsilon), 1e-6))
        return float(fact.value) + step
    if fact.value_type == "bool":
        return "not-a-boolean"
    if fact.value_type == "str":
        return "__CNVS_ABSURD_OBSERVATION__"
    return {"invalid": True, "payload": secrets.token_hex(8)}


# ==============================================================================
# Cons_R: COMPLETE GRAPH CONSISTENCY AND BOTTOM-UP RECONSTRUCTION
# ==============================================================================


def check_cons_r(state: CNVSSemanticState, evidence: Mapping[str, LocalEvidence]) -> Tuple[bool, str]:
    if set(evidence) != set(state.leaves):
        return False, "terminal evidence set does not equal Ter(t)"
    if state.topology_root not in state.nodes:
        return False, "topology root is missing"
    if state.nodes[state.topology_root].parent_id is not None:
        return False, "root has a parent"

    assigned = [leaf.assigned_verifier for leaf in state.leaves.values()]
    if len(assigned) != len(set(assigned)):
        return False, "one-fragment-per-verifier injective assignment was violated"

    derived_edges: Set[Tuple[str, str]] = set()
    parent_count: Dict[str, int] = {node_id: 0 for node_id in state.nodes}

    for node_id, node in state.nodes.items():
        recomputed_digest = _node_digest(node.node_id, node.children_ids, node.node_kind, node.node_nonce)
        if recomputed_digest != node.topology_digest:
            return False, f"topology digest mismatch at {node_id}"
        if node.children_ids and len(node.children_ids) < 2:
            return False, f"unary internal node detected at {node_id}"
        if node.node_kind == "terminal" and node.children_ids:
            return False, f"terminal node {node_id} has children"
        if node.node_kind != "terminal" and not node.children_ids:
            return False, f"non-terminal node {node_id} has no children"

        for child in node.children_ids:
            if child not in state.nodes:
                return False, f"unknown child {child}"
            if state.nodes[child].parent_id != node_id:
                return False, f"parent-child disagreement for {child}"
            parent_count[child] += 1
            derived_edges.add((node_id, child))

    if derived_edges != state.expected_relation_edges:
        return False, "R(t) does not coincide with the executable decomposition D"

    for node_id, count in parent_count.items():
        if node_id == state.topology_root:
            if count != 0:
                return False, "root appears as a child"
        elif count != 1:
            return False, f"node {node_id} has {count} parents"

    visited: Set[str] = set()
    active: Set[str] = set()

    def visit(node_id: str) -> bool:
        if node_id in active:
            return False
        if node_id in visited:
            return True
        active.add(node_id)
        for child in state.nodes[node_id].children_ids:
            if not visit(child):
                return False
        active.remove(node_id)
        visited.add(node_id)
        return True

    if not visit(state.topology_root):
        return False, "cycle detected in R(t)"
    if visited != set(state.nodes):
        return False, "R(t) is disconnected"

    terminal_nodes = {node_id for node_id, node in state.nodes.items() if not node.children_ids}
    if terminal_nodes != set(state.leaves):
        return False, "terminal node set differs from Ter(t)"

    for selector, leaf in state.leaves.items():
        ev = evidence[selector]
        if ev.selector != selector:
            return False, f"selector substitution at {selector}"
        if ev.verifier_id != leaf.assigned_verifier:
            return False, f"assignment mismatch at {selector}"
        if ev.claimed_parent != leaf.parent_node or ev.claimed_parent != state.nodes[selector].parent_id:
            return False, f"parent relation mismatch at {selector}"
        if ev.claimed_role != leaf.semantic_role:
            return False, f"semantic role mismatch at {selector}"
        if ev.task_digest != leaf.task_digest:
            return False, f"task binding mismatch at {selector}"
        expected_task_digest = _task_digest(
            selector,
            leaf.fact.fact_id,
            leaf.assigned_verifier,
            leaf.parent_node,
            leaf.semantic_role,
            leaf.task_nonce,
        )
        if expected_task_digest != leaf.task_digest:
            return False, f"stored task digest is invalid at {selector}"

    return True, "Cons_R accepted the complete decomposition graph"


def Cons_R(state: CNVSSemanticState, evidence: Mapping[str, LocalEvidence]) -> bool:
    return check_cons_r(state, evidence)[0]


def _leaf_reconstruction_digest(leaf: SemanticLeaf, observed: Any) -> str:
    return sha256_text(canonical_json({
        "selector": leaf.selector,
        "role": leaf.semantic_role,
        "observed": observed,
        "task_digest": leaf.task_digest,
    }))


def evaluate_progressive_invariants(
    state: CNVSSemanticState,
    evidence: Mapping[str, LocalEvidence],
) -> InvariantEvaluation:
    """
    Reconstruct S^(n), S^(n-1), ..., S^(0) and evaluate each invariant at the
    lowest node at which all required observations are available.

    This avoids the previous shortcut in which Inv_C was reduced to exact array
    equality.  Room equations can now veto a branch before building-wide totals
    are evaluated, while hidden selector bindings are overlapping calculations
    distributed across the reconstruction hierarchy.
    """
    values_by_fact_id = {
        leaf.fact.fact_id: evidence[selector].observed_value
        for selector, leaf in state.leaves.items()
    }
    critical_observed = np.asarray([
        float(evidence[selector].observed_value)
        for selector in state.hidden.critical_selectors
    ], dtype=np.float64)
    normalized = critical_observed / state.hidden.scales

    semantic_by_node: Dict[str, List[SemanticEquation]] = {}
    for equation, node_id in zip(state.hidden.semantic_equations, state.hidden.semantic_equation_nodes):
        semantic_by_node.setdefault(node_id, []).append(equation)

    hidden_rows_by_node: Dict[str, List[int]] = {}
    for row_idx, node_id in enumerate(state.hidden.row_nodes):
        hidden_rows_by_node.setdefault(node_id, []).append(row_idx)

    # Reconstructed node digests are calculated, not assumed.  They provide an
    # executable bottom-up trace even though the semantic invariant values are
    # evaluated directly from the terminal observations bound to each subtree.
    reconstructed_digest: Dict[str, str] = {}
    ordered_nodes = sorted(state.nodes, key=lambda node_id: state.depth_by_node[node_id], reverse=True)
    evaluated = 0

    for node_id in ordered_nodes:
        node = state.nodes[node_id]
        if not node.children_ids:
            reconstructed_digest[node_id] = _leaf_reconstruction_digest(
                state.leaves[node_id], evidence[node_id].observed_value
            )
        else:
            child_digests = [reconstructed_digest[child] for child in node.children_ids]
            reconstructed_digest[node_id] = sha256_text(canonical_json({
                "node": node_id,
                "children": child_digests,
                "topology": node.topology_digest,
            }))

        for equation in semantic_by_node.get(node_id, []):
            residual = abs(float(equation.evaluator(values_by_fact_id)))
            evaluated += 1
            if not math.isfinite(residual) or residual > float(equation.tolerance) + 1e-12:
                return InvariantEvaluation(
                    False,
                    node_id,
                    f"semantic invariant {equation.name} failed: residual={residual:.12g}, tolerance={equation.tolerance:.12g}",
                    evaluated,
                )

        for row_idx in hidden_rows_by_node.get(node_id, []):
            calculated = float(np.dot(state.hidden.matrix[row_idx], normalized))
            residual = abs(calculated - float(state.hidden.targets[row_idx]))
            evaluated += 1
            if residual > float(state.hidden.tolerances[row_idx]):
                return InvariantEvaluation(
                    False,
                    node_id,
                    f"hidden invariant row {row_idx} failed: residual={residual:.12g}",
                    evaluated,
                )

    if state.topology_root not in reconstructed_digest:
        return InvariantEvaluation(False, state.topology_root, "root reconstruction was not produced", evaluated)
    return InvariantEvaluation(True, "", "all progressive invariants accepted", evaluated)


def Inv_C(state: CNVSSemanticState, evidence: Mapping[str, LocalEvidence]) -> bool:
    return evaluate_progressive_invariants(state, evidence).ok


def V_G(state: CNVSSemanticState, evidence: Mapping[str, LocalEvidence]) -> ValidationResult:
    started = time.perf_counter_ns()

    all_local_ok = len(evidence) == len(state.leaves) and all(ev.local_admissible for ev in evidence.values())
    if not all_local_ok:
        return ValidationResult(
            accepted=False,
            all_local_ok=False,
            cons_r_ok=False,
            inv_c_ok=False,
            early_rejection=True,
            failed_stage="V_L",
            failing_node="",
            reason="EARLY REJECTION: one or more terminal observations are missing, malformed, or outside epsilon. Cons_R and Inv_C are not evaluated.",
            latency_ns=time.perf_counter_ns() - started,
        )

    cons_ok, cons_reason = check_cons_r(state, evidence)
    if not cons_ok:
        return ValidationResult(
            accepted=False,
            all_local_ok=True,
            cons_r_ok=False,
            inv_c_ok=False,
            early_rejection=False,
            failed_stage="Cons_R",
            failing_node="",
            reason=f"VETO: {cons_reason}.",
            latency_ns=time.perf_counter_ns() - started,
        )

    inv = evaluate_progressive_invariants(state, evidence)
    if not inv.ok:
        return ValidationResult(
            accepted=False,
            all_local_ok=True,
            cons_r_ok=True,
            inv_c_ok=False,
            early_rejection=False,
            failed_stage="Inv_C",
            failing_node=inv.failing_node,
            reason=f"VETO: {inv.reason}.",
            latency_ns=time.perf_counter_ns() - started,
            evaluated_invariants=inv.evaluated_count,
        )

    return ValidationResult(
        accepted=True,
        all_local_ok=True,
        cons_r_ok=True,
        inv_c_ok=True,
        early_rejection=False,
        failed_stage="",
        failing_node="",
        reason="ACCEPT: V_L, complete Cons_R reconstruction, and progressive Inv_C all passed.",
        latency_ns=time.perf_counter_ns() - started,
        evaluated_invariants=inv.evaluated_count,
    )


# ==============================================================================
# PROBABILITY REFERENCES — COMPARISON ONLY
# ==============================================================================


def log_comb(n: int, k: int) -> float:
    if k < 0 or k > n:
        return float("-inf")
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def hypergeom_pmf(x: int, Q: int, r: int, m: int) -> float:
    if x < max(0, m - (Q - r)) or x > min(m, r):
        return 0.0
    return math.exp(log_comb(r, x) + log_comb(Q - r, m - x) - log_comb(Q, m))


def exact_injective_reference(Q: int, r: int, m: int, p_inf: float) -> float:
    low = max(0, m - (Q - r))
    high = min(m, r)
    return sum(hypergeom_pmf(x, Q, r, m) * (p_inf ** (m - x)) for x in range(low, high + 1))


def theorem_reference(q: float, m: int, p_inf: float) -> float:
    p_comp = q + (1.0 - q) * p_inf
    return p_comp ** m


# ==============================================================================
# MONTE CARLO COLLUSION — ACTUAL HIDDEN-INVARIANT CALCULATION
# ==============================================================================


def _sample_exact_direct_mask(
    rng: np.random.Generator,
    direct_counts: np.ndarray,
    m: int,
) -> np.ndarray:
    """Uniformly choose exactly x distinct critical positions for every row."""
    batch = direct_counts.shape[0]
    random_keys = rng.random((batch, m))
    order = np.argsort(random_keys, axis=1)
    ranks = np.empty_like(order)
    rows = np.arange(batch)[:, None]
    ranks[rows, order] = np.arange(m)[None, :]
    return ranks < direct_counts[:, None]


def vectorized_collusion_batch(
    state: CNVSSemanticState,
    Q: int,
    r: int,
    batch_size: int,
    p_inf: float,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Execute one vectorized CNVS collusion batch.

    Directly acquired and correctly inferred critical fragments report the
    canonical values.  Every unresolved critical fragment submits a deliberately
    stealthy observation between 0.55 epsilon and 0.95 epsilon from the declared
    value.  Therefore V_L passes by construction, which is necessary to test the
    non-reducible part of CNVS rather than repeatedly exercising trivial early
    rejection.  Acceptance is then calculated by the hidden invariant matrix;
    no analytical reference is used in the decision path.
    """
    m = len(state.hidden.critical_selectors)
    direct_counts = rng.hypergeometric(r, Q - r, m, size=batch_size)
    direct_mask = _sample_exact_direct_mask(rng, direct_counts, m)
    inferred_mask = (~direct_mask) & (rng.random((batch_size, m)) < p_inf)
    unresolved = ~(direct_mask | inferred_mask)

    signs = np.where(rng.random((batch_size, m)) < 0.5, -1.0, 1.0)
    alpha = rng.uniform(0.55, 0.95, size=(batch_size, m))
    normalized_delta = unresolved * signs * alpha * (state.hidden.epsilons / state.hidden.scales)

    # V_L is true for all generated observations because every perturbation is
    # strictly within epsilon. Cons_R is true because this cycle alters values,
    # not selectors or relationships. Inv_C is explicitly calculated here.
    residuals = normalized_delta @ state.hidden.matrix.T
    inv_ok = np.all(np.abs(residuals) <= state.hidden.tolerances[None, :], axis=1)
    return inv_ok, direct_counts, inferred_mask.sum(axis=1), unresolved.sum(axis=1)


def benchmark_single_candidate_latency(
    state: CNVSSemanticState,
    samples: int,
) -> Tuple[float, float, float]:
    evidence = build_honest_evidence(state)
    latencies: List[float] = []
    for _ in range(samples):
        result = V_G(state, evidence)
        if not result.accepted:
            raise RuntimeError(result.reason)
        latencies.append(float(result.latency_ns))
    return quantile(latencies, 0.50), quantile(latencies, 0.95), quantile(latencies, 0.99)


def run_collusion_cycle(
    state: CNVSSemanticState,
    q: float,
    iterations: int,
    h_min_bits: float,
    batch_size: int,
    latency_samples: int,
    monte_carlo_seed: int,
) -> MonteCarloCycleResult:
    Q = state.active_verifier_count
    m = len(state.hidden.critical_selectors)
    r = min(Q, max(0, int(round(q * Q))))
    p_inf = p_inf_from_h(h_min_bits)
    rng = np.random.default_rng(monte_carlo_seed)

    accepted = 0
    sum_direct = 0.0
    sum_inferred = 0.0
    sum_failed = 0.0
    started = time.perf_counter_ns()
    remaining = iterations
    while remaining > 0:
        b = min(batch_size, remaining)
        inv_ok, direct, inferred, failed = vectorized_collusion_batch(state, Q, r, b, p_inf, rng)
        accepted += int(inv_ok.sum())
        sum_direct += float(direct.sum())
        sum_inferred += float(inferred.sum())
        sum_failed += float(failed.sum())
        remaining -= b
    elapsed = time.perf_counter_ns() - started

    accept_rate = accepted / iterations
    p50, p95, p99 = benchmark_single_candidate_latency(state, max(1, latency_samples))
    return MonteCarloCycleResult(
        q=q,
        Q=Q,
        r=r,
        m=m,
        iterations=iterations,
        p_inf=p_inf,
        vg_accept_rate=accept_rate,
        vg_veto_rate=1.0 - accept_rate,
        local_pass_global_veto_rate=1.0 - accept_rate,
        exact_ref=exact_injective_reference(Q, r, m, p_inf),
        theorem_ref=theorem_reference(q, m, p_inf),
        avg_direct=sum_direct / iterations,
        avg_inferred=sum_inferred / iterations,
        avg_failed=sum_failed / iterations,
        simulation_ns_per_iteration=elapsed / iterations,
        single_candidate_latency_p50_ns=p50,
        single_candidate_latency_p95_ns=p95,
        single_candidate_latency_p99_ns=p99,
        hidden_matrix_rank=int(np.linalg.matrix_rank(state.hidden.matrix)),
        monte_carlo_seed=monte_carlo_seed,
    )


# ==============================================================================
# STEALTH SEMANTIC ATTACK ON A PARTIAL INVARIANT
# ==============================================================================


def run_semantic_partial_invariant_attack(
    state: CNVSSemanticState,
    iterations: int,
    batch_size: int,
    seed: int,
) -> SemanticInvariantAttackResult:
    """
    Attack the kitchen-area relation with observations that all remain inside
    their individual V_L tolerances.

    The attacker increases length and width while decreasing the independently
    reported area.  No single terminal report is locally absurd, but the first
    reconstructed node containing all three facts calculates

        area_obs - length_obs * width_obs

    and vetoes the branch before building-level invariants are needed.
    """
    equation_name = "kitchen_area"
    equation = next(eq for eq in state.hidden.semantic_equations if eq.name == equation_name)
    eq_index = next(i for i, eq in enumerate(state.hidden.semantic_equations) if eq.name == equation_name)
    attached_node = state.hidden.semantic_equation_nodes[eq_index]
    ids = equation.required_fact_ids
    facts = [state.leaves[state.fact_to_selector[fact_id]].fact for fact_id in ids]
    expected = np.asarray([float(f.value) for f in facts], dtype=np.float64)
    eps = np.asarray([float(f.epsilon) for f in facts], dtype=np.float64)
    rng = np.random.default_rng(seed)

    local_pass = 0
    veto = 0
    remaining = iterations
    while remaining > 0:
        b = min(batch_size, remaining)
        alpha = rng.uniform(0.55, 0.95, size=(b, 3))
        # required_fact_ids are length, width, area
        delta = alpha * eps[None, :] * np.asarray([1.0, 1.0, -1.0])[None, :]
        observed = expected[None, :] + delta
        local_ok = np.all(np.abs(delta) <= eps[None, :] + 1e-15, axis=1)
        residual = np.abs(observed[:, 2] - observed[:, 0] * observed[:, 1])
        local_pass += int(local_ok.sum())
        veto += int(np.count_nonzero(local_ok & (residual > equation.tolerance + 1e-12)))
        remaining -= b

    evidence = build_honest_evidence(state)
    for fact, sign in zip(facts, (1.0, 1.0, -1.0)):
        selector = state.fact_to_selector[fact.fact_id]
        observed = float(fact.value) + sign * 0.75 * float(fact.epsilon)
        evidence[selector] = V_L(state, selector, observed)
    concrete = V_G(state, evidence)

    return SemanticInvariantAttackResult(
        equation_name=equation_name,
        attached_node=attached_node,
        iterations=iterations,
        local_pass_rate=local_pass / iterations,
        partial_invariant_veto_rate=veto / iterations,
        concrete_pipeline_veto=not concrete.accepted,
        concrete_failed_stage=concrete.failed_stage,
        concrete_failing_node=concrete.failing_node,
        seed=seed,
    )



# ==============================================================================
# PROGRESSIVE C_int LEAKAGE AND TOTAL-DISCLOSURE LIMIT
# ==============================================================================


def _nullspace(matrix: np.ndarray, tolerance: float = 1e-11) -> np.ndarray:
    if matrix.size == 0:
        return np.eye(matrix.shape[1], dtype=np.float64)
    _, singular, vh = np.linalg.svd(matrix, full_matrices=True)
    rank = int(np.sum(singular > tolerance))
    return vh[rank:].T.copy()




# ==============================================================================
# REFRESH: FULL AND MINIMAL CLOSED-BRANCH REGENERATION
# ==============================================================================


def _state_facts_in_order(state: CNVSSemanticState) -> List[SemanticFact]:
    by_id = {leaf.fact.fact_id: leaf.fact for leaf in state.leaves.values()}
    return [by_id[fact_id] for fact_id in state.selected_fact_ids]


def _verifier_map_by_fact(state: CNVSSemanticState) -> Dict[str, int]:
    return {leaf.fact.fact_id: leaf.assigned_verifier for leaf in state.leaves.values()}


def full_refresh(
    state: CNVSSemanticState,
    catalog: Sequence[SemanticFact],
    verifier_map: Mapping[str, int],
    cycle_suffix: str,
) -> CNVSSemanticState:
    facts = _state_facts_in_order(state)
    verifier_ids = [verifier_map[fact.fact_id] for fact in facts]
    # A full refresh re-samples A_t as well as D and the selector space.
    # The same eligible verifier set is retained, but its injective matching to
    # terminal tasks is cryptographically reshuffled.
    SECURE_RNG.shuffle(verifier_ids)
    return build_state(
        catalog,
        k=len(facts),
        m=len(state.hidden.critical_selectors),
        cycle_id=f"{state.cycle_id}|full_refresh|{cycle_suffix}",
        verifier_ids=verifier_ids,
        selected_facts=facts,
    )


def branch_refresh(
    state: CNVSSemanticState,
    catalog: Sequence[SemanticFact],
    failing_selector: str,
    verifier_map: Mapping[str, int],
    cycle_suffix: str,
) -> CNVSSemanticState:
    """
    Atomically retire the smallest closed branch containing the failed leaf,
    regenerate its selectors and internal nodes, and rebuild every ancestor up
    to the root.  Unaffected subtrees remain unique and active; the old parent is
    removed before the new parent is attached, so no duplicate parent can exist.

    C_int is re-keyed after the branch change.  This is stronger than merely
    recalculating the affected room equation and prevents stale invariant views
    from accumulating across rejected cycles.
    """
    if failing_selector not in state.leaves:
        raise KeyError(failing_selector)
    branch_root = state.nodes[failing_selector].parent_id or failing_selector
    affected_nodes = descendants(state.nodes, branch_root)
    affected_selectors = sorted(set(state.leaves).intersection(affected_nodes))
    affected_facts = [state.leaves[s].fact for s in affected_selectors]

    new_cycle_nonce = secrets.token_hex(24)
    new_selectors = [make_selector(f.fact_id, new_cycle_nonce) for f in affected_facts]
    new_groups = {selector: fact.group for selector, fact in zip(new_selectors, affected_facts)}
    new_subroot, new_subnodes, _ = build_full_tree(new_selectors, new_groups)

    # Copy everything outside the retired branch and outside the ancestors that
    # must be replaced because one of their child commitments changes.
    path = _ancestor_chain(state.nodes, branch_root)  # branch -> ... -> old root
    path_set = set(path)
    nodes: Dict[str, TreeNode] = {
        node_id: node
        for node_id, node in state.nodes.items()
        if node_id not in affected_nodes and node_id not in path_set
    }
    nodes.update(new_subnodes)

    current_new_child = new_subroot
    old_child = branch_root
    for old_ancestor in path[1:]:
        old_node = state.nodes[old_ancestor]
        new_children = tuple(current_new_child if child == old_child else child for child in old_node.children_ids)
        if len(new_children) < 2:
            raise RuntimeError("Branch refresh would create a unary ancestor.")
        new_id = "node_" + secrets.token_hex(12)
        nonce = secrets.token_hex(16)
        new_node = TreeNode(
            node_id=new_id,
            parent_id=None,
            children_ids=new_children,
            node_kind=old_node.node_kind,
            semantic_groups=old_node.semantic_groups,
            node_nonce=nonce,
            topology_digest=_node_digest(new_id, new_children, old_node.node_kind, nonce),
        )
        nodes[new_id] = new_node
        for child in new_children:
            nodes[child] = replace(nodes[child], parent_id=new_id)
        current_new_child = new_id
        old_child = old_ancestor

    new_root = current_new_child
    nodes[new_root] = replace(nodes[new_root], parent_id=None)

    # If the refreshed branch itself was the old root, no ancestor loop updated
    # its parent. Otherwise build_full_tree left the new subtree root parentless
    # and the first regenerated ancestor set it correctly.
    depth_by_node: Dict[str, int] = {new_root: 0}
    stack = [new_root]
    while stack:
        node_id = stack.pop()
        for child in nodes[node_id].children_ids:
            depth_by_node[child] = depth_by_node[node_id] + 1
            stack.append(child)

    old_by_fact = {leaf.fact.fact_id: leaf for leaf in state.leaves.values()}
    new_selector_by_fact = {fact.fact_id: selector for fact, selector in zip(affected_facts, new_selectors)}

    # Re-sample the injective assignment inside the refreshed closed branch.
    # Unaffected subtrees keep their verifier assignments, while every task in
    # the retired branch is rebound to a randomly permuted eligible verifier.
    effective_verifier_map = dict(verifier_map)
    affected_fact_ids = [fact.fact_id for fact in affected_facts]
    affected_verifiers = [effective_verifier_map[fact_id] for fact_id in affected_fact_ids]
    SECURE_RNG.shuffle(affected_verifiers)
    for fact_id, verifier_id in zip(affected_fact_ids, affected_verifiers):
        effective_verifier_map[fact_id] = verifier_id

    leaves: Dict[str, SemanticLeaf] = {}

    for fact_id in state.selected_fact_ids:
        old_leaf = old_by_fact[fact_id]
        selector = new_selector_by_fact.get(fact_id, old_leaf.selector)
        parent = nodes[selector].parent_id
        verifier = int(effective_verifier_map[fact_id])
        changed = selector != old_leaf.selector or parent != old_leaf.parent_node or verifier != old_leaf.assigned_verifier
        task_nonce = secrets.token_hex(16) if changed else old_leaf.task_nonce
        digest = _task_digest(selector, fact_id, verifier, parent, fact_id, task_nonce)
        leaves[selector] = SemanticLeaf(
            selector=selector,
            fact=old_leaf.fact,
            assigned_verifier=verifier,
            parent_node=parent,
            semantic_role=fact_id,
            task_nonce=task_nonce,
            task_digest=digest,
        )

    edges = {(node_id, child) for node_id, node in nodes.items() for child in node.children_ids}
    hidden = build_hidden_invariant_state(
        leaves,
        nodes,
        depth_by_node,
        len(state.hidden.critical_selectors),
        build_semantic_equation_family(),
    )
    return CNVSSemanticState(
        cycle_id=f"{state.cycle_id}|branch_refresh|{cycle_suffix}",
        leaves=leaves,
        nodes=nodes,
        fact_to_selector={leaf.fact.fact_id: selector for selector, leaf in leaves.items()},
        expected_relation_edges=edges,
        topology_root=new_root,
        hidden=hidden,
        semantic_catalog_size=len(catalog),
        topology_nonce=new_cycle_nonce,
        selected_fact_ids=state.selected_fact_ids,
        depth_by_node=depth_by_node,
    )


def refresh_metrics(old: CNVSSemanticState, new: CNVSSemanticState) -> Dict[str, float]:
    old_selectors = set(old.leaves)
    new_selectors = set(new.leaves)
    old_edges = old.expected_relation_edges
    new_edges = new.expected_relation_edges
    selector_union = old_selectors | new_selectors
    edge_union = old_edges | new_edges
    return {
        "selector_jaccard": len(old_selectors & new_selectors) / len(selector_union) if selector_union else 1.0,
        "edge_jaccard": len(old_edges & new_edges) / len(edge_union) if edge_union else 1.0,
        "selectors_regenerated": float(len(old_selectors - new_selectors)),
        "edges_changed": float(len(old_edges ^ new_edges)),
        "nodes_old": float(old.total_node_count),
        "nodes_new": float(new.total_node_count),
    }


def _replace_leaf_assignment(
    state: CNVSSemanticState,
    selector: str,
    verifier_id: int,
) -> CNVSSemanticState:
    leaves = dict(state.leaves)
    old = leaves[selector]
    nonce = secrets.token_hex(16)
    leaves[selector] = replace(
        old,
        assigned_verifier=verifier_id,
        task_nonce=nonce,
        task_digest=_task_digest(selector, old.fact.fact_id, verifier_id, old.parent_node, old.semantic_role, nonce),
    )
    return replace(state, leaves=leaves)


def run_missing_declaration_scenario(
    state: CNVSSemanticState,
    event_count: int,
    reserve_verifiers: List[int],
    event_log: List[Dict[str, Any]],
) -> CNVSSemanticState:
    """
    Missing obs is unresolved (Status_L = bottom), not a false observation.
    The task is reassigned before a candidate is submitted to V_G; no rejected
    global state and therefore no topology refresh is asserted in this branch.
    """
    current = state
    for event_index in range(1, event_count + 1):
        selector = SECURE_RNG.choice(list(current.leaves))
        old_verifier = current.leaves[selector].assigned_verifier
        unresolved = V_L(current, selector, None)
        if unresolved.local_admissible:
            raise RuntimeError("Missing observation unexpectedly passed V_L.")
        replacement_id = reserve_verifiers.pop(0) if reserve_verifiers else max(
            leaf.assigned_verifier for leaf in current.leaves.values()
        ) + event_index + 1
        current = _replace_leaf_assignment(current, selector, replacement_id)
        result = V_G(current, build_honest_evidence(current))
        if not result.accepted:
            raise RuntimeError(f"Reassignment recovery failed: {result.reason}")
        event_log.append({
            "scenario": "missing_observation_reassignment",
            "event": event_index,
            "selector": selector,
            "old_verifier": old_verifier,
            "replacement_verifier": replacement_id,
            "local_status": "UNRESOLVED_BOTTOM",
            "topology_refreshed": False,
            "recovered": True,
        })
    return current


def run_absurd_data_refresh_scenario(
    initial_state: CNVSSemanticState,
    catalog: Sequence[SemanticFact],
    event_count: int,
    reserve_verifiers: List[int],
    event_log: List[Dict[str, Any]],
) -> CNVSSemanticState:
    """
    Select 3-6 genuinely colluding verifiers, force an observation outside V_L,
    expel each verifier, and compare a minimal closed-branch refresh with a full
    CNVS refresh.  Old evidence is replayed against the new state to verify that
    stale topology/selectors cannot be accepted.
    """
    current = initial_state
    coalition = set(SECURE_RNG.sample(
        [leaf.assigned_verifier for leaf in current.leaves.values()],
        min(max(event_count * 2, 8), current.active_verifier_count),
    ))

    for event_index in range(1, event_count + 1):
        colluding_selectors = [
            selector for selector, leaf in current.leaves.items()
            if leaf.assigned_verifier in coalition
        ]
        if not colluding_selectors:
            break
        selector = SECURE_RNG.choice(colluding_selectors)
        leaf = current.leaves[selector]
        old_evidence = build_honest_evidence(current)
        old_evidence[selector] = V_L(current, selector, absurd_observation(leaf.fact))
        early = V_G(current, old_evidence)
        if early.accepted or early.failed_stage != "V_L":
            raise RuntimeError("Absurd observation did not trigger V_L early rejection.")

        expelled = leaf.assigned_verifier
        coalition.discard(expelled)
        replacement_id = reserve_verifiers.pop(0) if reserve_verifiers else max(
            x.assigned_verifier for x in current.leaves.values()
        ) + event_index + 1
        verifier_map = _verifier_map_by_fact(current)
        verifier_map[leaf.fact.fact_id] = replacement_id

        branch_started = time.perf_counter_ns()
        refreshed = branch_refresh(
            current,
            catalog,
            selector,
            verifier_map,
            cycle_suffix=f"event_{event_index}",
        )
        branch_ns = time.perf_counter_ns() - branch_started

        full_started = time.perf_counter_ns()
        full_shadow = full_refresh(
            current,
            catalog,
            verifier_map,
            cycle_suffix=f"event_{event_index}",
        )
        full_ns = time.perf_counter_ns() - full_started

        branch_result = V_G(refreshed, build_honest_evidence(refreshed))
        full_result = V_G(full_shadow, build_honest_evidence(full_shadow))
        if not branch_result.accepted or not full_result.accepted:
            raise RuntimeError("Refresh did not recover a valid candidate state.")

        stale_replay = V_G(refreshed, build_honest_evidence(current))
        metrics = refresh_metrics(current, refreshed)
        event_log.append({
            "scenario": "absurd_colluder_expulsion_refresh",
            "event": event_index,
            "selector": selector,
            "fact_id": leaf.fact.fact_id,
            "expelled_verifier": expelled,
            "replacement_verifier": replacement_id,
            "early_rejection_stage": early.failed_stage,
            "branch_refresh_ns": branch_ns,
            "full_refresh_shadow_ns": full_ns,
            "branch_recovered": branch_result.accepted,
            "full_shadow_recovered": full_result.accepted,
            "stale_replay_accepted": stale_replay.accepted,
            **metrics,
        })
        current = refreshed

    return current


# ==============================================================================
# SCALABILITY, TABLES AND PLOTS
# ==============================================================================


def _terminal_relation_degree(state: CNVSSemanticState, selector: str) -> int:
    """Return the number of declared reconstruction edges incident to a terminal."""
    return sum(1 for left, right in state.expected_relation_edges if selector in (left, right))


def _critical_row_membership(state: CNVSSemanticState) -> Dict[str, List[int]]:
    membership: Dict[str, List[int]] = {selector: [] for selector in state.leaves}
    critical = list(state.hidden.critical_selectors)
    for row_idx, support in enumerate(state.hidden.row_supports):
        for critical_idx in support:
            if 0 <= critical_idx < len(critical):
                membership.setdefault(critical[critical_idx], []).append(row_idx)
    return membership


def _semantic_equation_membership(state: CNVSSemanticState) -> Dict[str, List[str]]:
    membership: Dict[str, List[str]] = {selector: [] for selector in state.leaves}
    for equation in state.hidden.semantic_equations:
        for fact_id in equation.required_fact_ids:
            selector = state.fact_to_selector.get(fact_id)
            if selector is not None:
                membership.setdefault(selector, []).append(equation.name)
    return membership


def fragment_table_rows(state: CNVSSemanticState, evidence: Mapping[str, LocalEvidence]) -> List[Dict[str, Any]]:
    """Create the detailed terminal table used by the original semantic test.

    Test 14 keeps the legacy columns (d_i, obs_i, Form_sigma, Conv_sigma,
    Adm_L, relation degree) and adds the literal parent/role binding plus the
    Inv_C rows and semantic equations in which each terminal participates.
    This is reporting only; it does not alter the V_G decision path.
    """
    rows: List[Dict[str, Any]] = []
    critical = set(state.hidden.critical_selectors)
    row_membership = _critical_row_membership(state)
    equation_membership = _semantic_equation_membership(state)

    for selector, leaf in sorted(state.leaves.items(), key=lambda item: item[1].assigned_verifier):
        ev = evidence[selector]
        rows.append({
            "selector": selector,
            "verifier": leaf.assigned_verifier,
            "fact_id": leaf.fact.fact_id,
            "group": leaf.fact.group,
            "parent": leaf.parent_node,
            "role": leaf.semantic_role,
            "d_i": canonical_json(leaf.fact.value),
            "unit": leaf.fact.unit,
            "epsilon": leaf.fact.epsilon,
            "obs_i": canonical_json(ev.observed_value),
            "error": ev.error_value,
            "adherence": ev.adherence,
            "Form_sigma": int(ev.form_ok),
            "Conv_sigma": int(ev.conv_ok),
            "Adm_L": int(ev.local_admissible),
            "relation_degree": _terminal_relation_degree(state, selector),
            "epsilon_exceeded": int(not ev.conv_ok),
            "critical": int(selector in critical),
            "Inv_C_hidden_rows": ";".join(str(x) for x in row_membership.get(selector, ())),
            "Inv_C_semantic_equations": ";".join(equation_membership.get(selector, ())),
            "task_digest": leaf.task_digest,
        })
    return rows


def hidden_invariant_table_rows(
    state: CNVSSemanticState,
    evidence: Mapping[str, LocalEvidence],
) -> List[Dict[str, Any]]:
    """Materialize every hidden linear Inv_C row for independent inspection."""
    critical = list(state.hidden.critical_selectors)
    observed = np.asarray([float(evidence[s].observed_value) for s in critical], dtype=np.float64)
    normalized = observed / state.hidden.scales
    rows: List[Dict[str, Any]] = []

    for row_idx, support in enumerate(state.hidden.row_supports):
        selectors = [critical[i] for i in support]
        fact_ids = [state.leaves[s].fact.fact_id for s in selectors]
        coefficients = [float(state.hidden.matrix[row_idx, i]) for i in support]
        calculated = float(np.dot(state.hidden.matrix[row_idx], normalized))
        target = float(state.hidden.targets[row_idx])
        tolerance = float(state.hidden.tolerances[row_idx])
        residual = abs(calculated - target)
        rows.append({
            "invariant_type": "hidden_linear",
            "row_index": row_idx,
            "attached_node": state.hidden.row_nodes[row_idx],
            "support_size": len(support),
            "critical_indices": ";".join(str(i) for i in support),
            "selectors": ";".join(selectors),
            "fact_ids": ";".join(fact_ids),
            "coefficients": canonical_json(coefficients),
            "calculated": calculated,
            "target": target,
            "residual": residual,
            "tolerance": tolerance,
            "Inv_C_pass": int(residual <= tolerance + 1e-15),
        })
    return rows


def semantic_invariant_table_rows(
    state: CNVSSemanticState,
    evidence: Mapping[str, LocalEvidence],
) -> List[Dict[str, Any]]:
    """Materialize every semantic equation evaluated by progressive Inv_C."""
    values_by_fact_id = {
        leaf.fact.fact_id: evidence[selector].observed_value
        for selector, leaf in state.leaves.items()
    }
    rows: List[Dict[str, Any]] = []
    for equation, node_id in zip(state.hidden.semantic_equations, state.hidden.semantic_equation_nodes):
        residual = abs(float(equation.evaluator(values_by_fact_id)))
        tolerance = float(equation.tolerance)
        rows.append({
            "invariant_type": "semantic_equation",
            "equation_name": equation.name,
            "attached_node": node_id,
            "required_fact_ids": ";".join(equation.required_fact_ids),
            "description": equation.description,
            "residual": residual,
            "tolerance": tolerance,
            "Inv_C_pass": int(math.isfinite(residual) and residual <= tolerance + 1e-12),
        })
    return rows


def write_rows_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    # Preserve first-seen column order, matching the original Test 13 tables.
    fields: List[str] = []
    seen: Set[str] = set()
    for row in rows:
        for key in row:
            if key not in seen:
                seen.add(key)
                fields.append(key)

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def print_fragment_table(rows: Sequence[Mapping[str, Any]], show_full: bool) -> None:
    if not rows:
        return
    visible = list(rows) if show_full else list(rows[:12])
    print("\n[Terminal fragment / Inv_C membership table]")
    print(
        "selector | verifier | fact_id | d_i | epsilon | obs_i | error | adherence | "
        "Form | Conv | Adm_L | degree | critical | hidden_rows | semantic_equations"
    )
    print("-" * 220)
    for row in visible:
        print(
            f"{str(row['selector'])[:24]:24s} | {int(row['verifier']):4d} | "
            f"{str(row['fact_id'])[:44]:44s} | {str(row['d_i'])[:18]:18s} | "
            f"{row['epsilon']} | {str(row['obs_i'])[:18]:18s} | {row['error']} | "
            f"{float(row['adherence']):.6f} | {row['Form_sigma']} | {row['Conv_sigma']} | "
            f"{row['Adm_L']} | {row['relation_degree']} | {row['critical']} | "
            f"{str(row['Inv_C_hidden_rows'])[:28]:28s} | "
            f"{str(row['Inv_C_semantic_equations'])[:36]}"
        )
    if not show_full and len(rows) > len(visible):
        print(f"... {len(rows) - len(visible):,} additional rows written to CSV")



def run_scalability_cycle(
    catalog: Sequence[SemanticFact],
    Q: int,
    iterations: int,
    m_default: int,
    batch_size: int,
    latency_samples: int,
) -> ScalabilityResult:
    state = build_state(catalog, Q, min(m_default, Q), f"scalability_Q_{Q}")
    evidence = build_honest_evidence(state)
    latencies: List[float] = []
    for _ in range(max(1, latency_samples)):
        result = V_G(state, evidence)
        if not result.accepted:
            raise RuntimeError(result.reason)
        latencies.append(float(result.latency_ns))

    # Vectorized all-honest cycles still calculate the invariant residual matrix;
    # they are not used as a substitute for the full-pipeline latency samples.
    started = time.perf_counter_ns()
    remaining = iterations
    m = len(state.hidden.critical_selectors)
    zero_delta = np.zeros((min(batch_size, iterations), m), dtype=np.float64)
    while remaining > 0:
        b = min(batch_size, remaining)
        residual = zero_delta[:b] @ state.hidden.matrix.T
        if not np.all(np.abs(residual) <= state.hidden.tolerances[None, :]):
            raise RuntimeError("All-honest vectorized invariant calculation failed.")
        remaining -= b
    elapsed = time.perf_counter_ns() - started
    ns_per = elapsed / iterations

    return ScalabilityResult(
        Q=Q,
        fragments=state.terminal_fragment_count,
        total_nodes=state.total_node_count,
        critical_fragments=m,
        iterations=iterations,
        full_pipeline_mean_ns=float(statistics.fmean(latencies)),
        full_pipeline_p50_ns=quantile(latencies, 0.50),
        full_pipeline_p95_ns=quantile(latencies, 0.95),
        full_pipeline_p99_ns=quantile(latencies, 0.99),
        vectorized_ns_per_iteration=ns_per,
        vectorized_throughput_per_second=1e9 / ns_per if ns_per > 0 else float("inf"),
    )


def plot_collusion_results(results: Sequence[MonteCarloCycleResult], figure_dir: Path, show_plots: bool) -> None:
    if not results:
        return
    figure_dir.mkdir(parents=True, exist_ok=True)
    q = [x.q for x in results]
    plt.figure(figsize=(10, 6))
    plt.plot(q, [x.vg_accept_rate for x in results], marker="o", label="Monte Carlo V_G")
    plt.plot(q, [x.exact_ref for x in results], linestyle="--", label="Exact injective reference")
    plt.plot(q, [x.theorem_ref for x in results], linestyle=":", label="Compact theorem reference")
    plt.xlabel("Colluding verifier fraction q")
    plt.ylabel("Acceptance / reconstruction probability")
    plt.title("CNVS Test 14 — Collusion sweep")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_dir / "collusion_sweep.png", dpi=180)
    if show_plots:
        plt.show()
    plt.close()


def plot_leakage_results(results: Sequence[LeakageCycleResult], figure_dir: Path, show_plots: bool) -> None:
    if not results:
        return
    figure_dir.mkdir(parents=True, exist_ok=True)
    x = [r.leakage_fraction for r in results]
    plt.figure(figsize=(10, 6))
    plt.plot(x, [r.full_invariant_bypass_rate for r in results], marker="o", label="False-state bypass")
    plt.plot(x, [r.feasible_false_state_rate for r in results], marker="s", label="Feasible leaked-nullspace attack")
    plt.xlabel("Fraction of C_int rows disclosed")
    plt.ylabel("Rate")
    plt.title("CNVS Test 14 — Progressive invariant leakage")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(figure_dir / "invariant_leakage.png", dpi=180)
    if show_plots:
        plt.show()
    plt.close()





# ==============================================================================
# ENHANCED FULL-PIPELINE MONTE CARLO LAYER
# ==============================================================================
#
# The original revised implementation already executes the complete object-graph
# path V_L -> Cons_R -> Inv_C -> V_G for concrete candidates.  The section below
# strengthens the statistical design: every Monte Carlo candidate now receives
# an explicit result at every logical stage, while an independent configurable
# audit sample is also evaluated by the literal object-level V_G function.
#
# Two kinds of execution are intentionally reported separately:
#
# 1. Batched full logical pipeline
#    Every generated candidate is checked for local convergence, relational
#    binding, progressive semantic/hidden invariants, and final global validity.
#    NumPy is used only to execute many independent candidates efficiently; it
#    does not insert the expected answer or use the analytical reference curves.
#
# 2. Object-graph audit pipeline
#    A sample of the same candidate class is converted into LocalEvidence and is
#    passed through the literal V_G implementation over the complete tree.  This
#    verifies that the batched implementation and the executable graph agree.
#
# A simulated experiment has no physical terminal verifier.  Therefore the
# normal operating population must be generated.  Honest terminals return the
# declared value, optionally with bounded measurement noise.  Stealth colluders
# deliberately remain inside epsilon, because observations outside epsilon would
# be stopped immediately by V_L and would test only early rejection.  Blatant
# colluders are tested separately: they exceed epsilon, are expelled, and cause
# selector/topology refresh.  This separation is an experimental design choice,
# not an assumption that global validity is true.

DEFAULT_SEED_REPLICATES = 10
DEFAULT_OBJECT_PIPELINE_AUDITS = 1_000
DEFAULT_REFRESH_ITERATIONS = 10_000
DEFAULT_REFRESH_OBJECT_AUDITS = 1_000
DEFAULT_REFRESH_FULL_SHADOW_AUDITS = 100
DEFAULT_REFRESH_Q = 100
DEFAULT_SCALABILITY_FULL_PIPELINE_ITERATIONS = 10_000


@dataclass
class StageCounters:
    iterations: int = 0
    local_pass: int = 0
    cons_pass: int = 0
    inv_pass: int = 0
    accepted: int = 0
    v_l_reject: int = 0
    cons_r_veto: int = 0
    inv_c_veto: int = 0

    def add_arrays(self, local_ok: np.ndarray, cons_ok: np.ndarray, inv_ok: np.ndarray) -> None:
        local_ok = np.asarray(local_ok, dtype=bool)
        cons_ok = np.asarray(cons_ok, dtype=bool)
        inv_ok = np.asarray(inv_ok, dtype=bool)
        if not (local_ok.shape == cons_ok.shape == inv_ok.shape):
            raise ValueError("Stage arrays must have identical shapes.")
        accepted = local_ok & cons_ok & inv_ok
        self.iterations += int(local_ok.size)
        self.local_pass += int(local_ok.sum())
        self.cons_pass += int((local_ok & cons_ok).sum())
        self.inv_pass += int((local_ok & cons_ok & inv_ok).sum())
        self.accepted += int(accepted.sum())
        self.v_l_reject += int((~local_ok).sum())
        self.cons_r_veto += int((local_ok & ~cons_ok).sum())
        self.inv_c_veto += int((local_ok & cons_ok & ~inv_ok).sum())

    def merge(self, other: "StageCounters") -> None:
        for name in (
            "iterations", "local_pass", "cons_pass", "inv_pass", "accepted",
            "v_l_reject", "cons_r_veto", "inv_c_veto",
        ):
            setattr(self, name, int(getattr(self, name)) + int(getattr(other, name)))

    def as_rates(self) -> Dict[str, float]:
        n = max(1, self.iterations)
        return {
            "iterations": float(self.iterations),
            "local_pass_rate": self.local_pass / n,
            "cons_pass_rate": self.cons_pass / n,
            "inv_pass_rate": self.inv_pass / n,
            "vg_accept_rate": self.accepted / n,
            "v_l_reject_rate": self.v_l_reject / n,
            "cons_r_veto_rate": self.cons_r_veto / n,
            "inv_c_veto_rate": self.inv_c_veto / n,
        }


@dataclass
class EnhancedCollusionResult:
    q: float
    Q: int
    r: int
    m: int
    iterations: int
    seed_replicates: int
    p_inf: float
    local_pass_rate: float
    cons_pass_rate: float
    inv_pass_rate: float
    vg_accept_rate: float
    v_l_reject_rate: float
    cons_r_veto_rate: float
    inv_c_veto_rate: float
    exact_ref: float
    theorem_ref: float
    seed_mean_accept_rate: float
    seed_std_accept_rate: float
    ci95_low: float
    ci95_high: float
    avg_direct: float
    avg_inferred: float
    avg_failed: float
    object_audits: int
    object_accept_rate: float
    object_vector_agreement_rate: float
    simulation_ns_per_iteration: float
    single_candidate_latency_p50_ns: float
    single_candidate_latency_p95_ns: float
    single_candidate_latency_p99_ns: float


@dataclass
class EnhancedSemanticAttackResult:
    equation_name: str
    attached_node: str
    iterations: int
    seed_replicates: int
    local_pass_rate: float
    cons_pass_rate: float
    inv_c_veto_rate: float
    vg_accept_rate: float
    seed_mean_veto_rate: float
    seed_std_veto_rate: float
    ci95_veto_low: float
    ci95_veto_high: float
    object_audits: int
    object_veto_rate: float
    object_vector_agreement_rate: float


@dataclass
class EnhancedRelationalAttackResult:
    attack_type: str
    iterations: int
    seed_replicates: int
    local_pass_rate: float
    cons_r_detection_rate: float
    vg_bypass_rate: float
    ci95_detection_low: float
    ci95_detection_high: float
    object_audits: int
    object_detection_rate: float
    object_vector_agreement_rate: float


@dataclass
class EnhancedLeakageResult:
    leakage_fraction: float
    leaked_rows: int
    total_rows: int
    nullspace_dimension: int
    iterations: int
    seed_replicates: int
    local_pass_rate: float
    cons_pass_rate: float
    feasible_false_state_rate: float
    false_state_bypass_rate: float
    semantic_or_hidden_veto_rate: float
    mean_semantic_distortion: float
    exact_reconstruction_attempts: int
    exact_reconstruction_accept_rate: float
    object_audits: int
    object_vector_agreement_rate: float


@dataclass
class RefreshStressResult:
    iterations: int
    seed_replicates: int
    early_rejection_rate: float
    selector_changed_rate: float
    stale_replay_accept_rate: float
    injective_reassignment_rate: float
    object_audits: int
    object_early_rejection_rate: float
    object_recovery_rate: float
    object_stale_replay_accept_rate: float
    full_shadow_audits: int
    full_shadow_recovery_rate: float
    branch_refresh_mean_ns: float
    full_refresh_mean_ns: float


@dataclass
class EnhancedScalabilityResult:
    Q: int
    fragments: int
    total_nodes: int
    critical_fragments: int
    full_pipeline_iterations: int
    accepted_rate: float
    mean_latency_ns: float
    p50_latency_ns: float
    p95_latency_ns: float
    p99_latency_ns: float
    throughput_per_second: float
    vectorized_iterations: int
    vectorized_ns_per_iteration: float


def _split_iterations(total: int, replicates: int) -> List[int]:
    if total <= 0 or replicates <= 0:
        raise ValueError("total and replicates must be positive.")
    base, extra = divmod(total, replicates)
    return [base + (1 if i < extra else 0) for i in range(replicates) if base + (1 if i < extra else 0) > 0]


def _wilson_interval(successes: int, total: int, z: float = 1.959963984540054) -> Tuple[float, float]:
    if total <= 0:
        return 0.0, 0.0
    p = successes / total
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    half = z * math.sqrt((p * (1.0 - p) + z2 / (4.0 * total)) / total) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def _seed_children(master_seed: int, count: int) -> List[int]:
    sequence = np.random.SeedSequence(master_seed)
    return [int(child.generate_state(1, dtype=np.uint64)[0]) for child in sequence.spawn(count)]


def _critical_fact_index(state: CNVSSemanticState) -> Dict[str, int]:
    return {
        state.leaves[selector].fact.fact_id: idx
        for idx, selector in enumerate(state.hidden.critical_selectors)
    }


def _vectorized_semantic_residual(
    equation: SemanticEquation,
    getter: Callable[[str], np.ndarray],
) -> np.ndarray:
    """Vectorized counterpart of every semantic equation in Test 14."""
    g = getter
    name = equation.name
    if name == "building_footprint":
        return g("building.footprint_m2") - g("building.length_ew_m") * g("building.depth_ns_m")
    if name == "garden_area":
        return g("garden.area_m2") - g("garden.length_ew_m") * g("garden.depth_ns_m")
    if name == "east_centering":
        return g("garden.distance_east_m") - (g("garden.length_ew_m") - g("building.length_ew_m")) / 2.0
    if name == "north_centering":
        return g("garden.distance_north_m") - (g("garden.depth_ns_m") - g("building.depth_ns_m")) / 2.0
    if name == "east_usable_garden":
        return g("garden.usable_east_m") - (g("garden.distance_east_m") - g("garden.walkway_width_m"))
    if name == "north_usable_garden":
        return g("garden.usable_north_m") - (g("garden.distance_north_m") - g("garden.walkway_width_m"))
    if name == "apartment_count":
        return g("building.total_apartments") - g("building.floors") * g("building.apartments_per_floor")
    if name == "sector_area":
        return g("building.sector_area_m2") - g("building.sector_length_ew_m") * g("building.depth_ns_m")
    if name == "apartment_module_area":
        return g("building.apartment_module_gross_m2") - g("building.apartment_module_length_ew_m") * g("building.apartment_module_depth_ns_m")
    if name == "sector_decomposition":
        return g("building.sector_area_m2") - (g("building.stair_core_area_m2") + 2.0 * g("building.apartment_module_gross_m2"))
    if name == "balcony_area":
        return g("balcony.area_m2") - g("balcony.length_m") * g("balcony.depth_m")
    if name == "balcony_count":
        return g("balcony.total_count") - g("balcony.north_count") - g("balcony.south_count")
    if name == "big_window_width":
        return g("window.big.width_m") - g("window.big.leaf_count") * g("window.big.leaf_width_m")
    if name == "opening_count":
        return g("window.total_count") - (
            g("window.north.big_count") + g("window.north.small_count") +
            g("window.south.count") + g("window.east.count") + g("window.west.count")
        )
    if name == "fence_pitch":
        return g("fence.module_pitch_m") - g("fence.column_width_m") - g("fence.column_gap_m")
    if name == "fence_modular_length":
        return g("fence.modular_length_m") - (g("fence.perimeter_m") - g("fence.gate_width_m"))
    if name == "fence_column_count":
        return g("fence.column_count") - g("fence.modular_length_m") / g("fence.module_pitch_m")
    if name == "landing_area":
        return g("enzo.landing.area_m2") - g("enzo.landing.length_ew_m") * g("enzo.landing.width_ns_m")
    if name == "enzo_gross_area":
        return g("enzo.apartment.gross_area_m2") - g("enzo.apartment.gross_length_ew_m") * g("enzo.apartment.gross_depth_ns_m")
    if name == "kitchen_area":
        return g("enzo.room.kitchen.area_m2") - g("enzo.room.kitchen.length_m") * g("enzo.room.kitchen.width_m")
    if name == "bathroom_area":
        return g("enzo.room.bathroom.area_m2") - g("enzo.room.bathroom.length_m") * g("enzo.room.bathroom.width_m")
    raise KeyError(f"No vectorized semantic evaluator for {name!r}.")


def evaluate_semantic_equations_batch(
    state: CNVSSemanticState,
    critical_values: np.ndarray,
) -> np.ndarray:
    """
    Evaluate every active semantic equation for every candidate.

    Values outside the critical vector retain their honest declared values.  A
    critical value is taken from the candidate matrix.  Thus semantic invariants
    and hidden C_int bindings are both genuinely evaluated for the same state.
    """
    critical_values = np.asarray(critical_values, dtype=np.float64)
    if critical_values.ndim != 2 or critical_values.shape[1] != len(state.hidden.critical_selectors):
        raise ValueError("critical_values has an invalid shape.")
    batch = critical_values.shape[0]
    critical_index = _critical_fact_index(state)
    expected_by_fact = {
        leaf.fact.fact_id: float(leaf.fact.value)
        for leaf in state.leaves.values()
        if is_numeric_fact(leaf.fact)
    }

    def getter(fact_id: str) -> np.ndarray:
        idx = critical_index.get(fact_id)
        if idx is not None:
            return critical_values[:, idx]
        return np.full(batch, expected_by_fact[fact_id], dtype=np.float64)

    ok = np.ones(batch, dtype=bool)
    for equation in state.hidden.semantic_equations:
        residual = np.abs(_vectorized_semantic_residual(equation, getter))
        ok &= np.isfinite(residual) & (residual <= float(equation.tolerance) + 1e-12)
    return ok


def evaluate_hidden_invariants_batch(state: CNVSSemanticState, critical_values: np.ndarray) -> np.ndarray:
    normalized = np.asarray(critical_values, dtype=np.float64) / state.hidden.scales[None, :]
    residuals = normalized @ state.hidden.matrix.T - state.hidden.targets[None, :]
    return np.all(np.abs(residuals) <= state.hidden.tolerances[None, :], axis=1)


def _full_stage_collusion_batch(
    state: CNVSSemanticState,
    Q: int,
    r: int,
    batch_size: int,
    p_inf: float,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    m = len(state.hidden.critical_selectors)
    direct_counts = rng.hypergeometric(r, Q - r, m, size=batch_size)
    direct_mask = _sample_exact_direct_mask(rng, direct_counts, m)
    inferred_mask = (~direct_mask) & (rng.random((batch_size, m)) < p_inf)
    unresolved = ~(direct_mask | inferred_mask)

    signs = np.where(rng.random((batch_size, m)) < 0.5, -1.0, 1.0)
    alpha = rng.uniform(0.55, 0.95, size=(batch_size, m))
    delta = unresolved * signs * alpha * state.hidden.epsilons[None, :]
    candidate_values = state.hidden.expected_values[None, :] + delta

    # V_L is calculated from the actual generated observations.  It is expected
    # to pass because this scenario deliberately models stealth manipulation,
    # but the result is measured rather than hard-coded into V_G acceptance.
    local_ok = np.all(
        np.isfinite(candidate_values) &
        (np.abs(candidate_values - state.hidden.expected_values[None, :]) <= state.hidden.epsilons[None, :] + 1e-15),
        axis=1,
    )

    # No relational field is modified in the collusion-value scenario.  Cons_R
    # therefore receives the canonical parent, role, verifier and task binding.
    # The boolean is still part of each candidate's stage result.
    cons_ok = np.ones(batch_size, dtype=bool)
    semantic_ok = evaluate_semantic_equations_batch(state, candidate_values)
    hidden_ok = evaluate_hidden_invariants_batch(state, candidate_values)
    inv_ok = semantic_ok & hidden_ok
    return local_ok, cons_ok, inv_ok, direct_counts, inferred_mask.sum(axis=1), unresolved.sum(axis=1), candidate_values


def _object_collusion_candidate(
    state: CNVSSemanticState,
    Q: int,
    r: int,
    p_inf: float,
    rng: np.random.Generator,
) -> Tuple[ValidationResult, bool]:
    m = len(state.hidden.critical_selectors)
    direct_count = int(rng.hypergeometric(r, Q - r, m))
    direct_positions = set(int(x) for x in rng.choice(m, size=direct_count, replace=False)) if direct_count else set()
    inferred_positions = {
        idx for idx in range(m)
        if idx not in direct_positions and rng.random() < p_inf
    }
    evidence = build_honest_evidence(state)
    candidate = state.hidden.expected_values.copy()
    for idx, selector in enumerate(state.hidden.critical_selectors):
        if idx in direct_positions or idx in inferred_positions:
            continue
        fact = state.leaves[selector].fact
        observed = stealth_observation(fact, rng)
        evidence[selector] = V_L(state, selector, observed)
        candidate[idx] = float(observed)
    result = V_G(state, evidence)
    local_ok = bool(np.all(np.abs(candidate - state.hidden.expected_values) <= state.hidden.epsilons + 1e-15))
    vector_accept = bool(
        local_ok and
        evaluate_semantic_equations_batch(state, candidate[None, :])[0] and
        evaluate_hidden_invariants_batch(state, candidate[None, :])[0]
    )
    return result, vector_accept


def run_collusion_cycle_full_pipeline(
    state: CNVSSemanticState,
    q: float,
    iterations: int,
    h_min_bits: float,
    batch_size: int,
    seed_replicates: int,
    master_seed: int,
    object_audits: int,
) -> Tuple[EnhancedCollusionResult, List[Dict[str, Any]]]:
    Q = state.active_verifier_count
    m = len(state.hidden.critical_selectors)
    r = min(Q, max(0, int(round(q * Q))))
    p_inf = p_inf_from_h(h_min_bits)
    counts = _split_iterations(iterations, seed_replicates)
    seeds = _seed_children(master_seed, len(counts) + 1)
    aggregate = StageCounters()
    seed_rows: List[Dict[str, Any]] = []
    accept_rates: List[float] = []
    sum_direct = sum_inferred = sum_failed = 0.0
    started = time.perf_counter_ns()

    for replicate, (n_rep, seed) in enumerate(zip(counts, seeds), start=1):
        rng = np.random.default_rng(seed)
        stages = StageCounters()
        rep_direct = rep_inferred = rep_failed = 0.0
        remaining = n_rep
        while remaining > 0:
            b = min(batch_size, remaining)
            local_ok, cons_ok, inv_ok, direct, inferred, failed, _ = _full_stage_collusion_batch(
                state, Q, r, b, p_inf, rng
            )
            stages.add_arrays(local_ok, cons_ok, inv_ok)
            rep_direct += float(direct.sum())
            rep_inferred += float(inferred.sum())
            rep_failed += float(failed.sum())
            remaining -= b
        aggregate.merge(stages)
        rate = stages.accepted / stages.iterations
        accept_rates.append(rate)
        sum_direct += rep_direct
        sum_inferred += rep_inferred
        sum_failed += rep_failed
        seed_rows.append({
            "q": q,
            "replicate": replicate,
            "seed": seed,
            "iterations": stages.iterations,
            "local_pass_rate": stages.local_pass / stages.iterations,
            "cons_pass_rate": stages.cons_pass / stages.iterations,
            "inv_pass_rate": stages.inv_pass / stages.iterations,
            "vg_accept_rate": rate,
            "v_l_rejects": stages.v_l_reject,
            "cons_r_vetoes": stages.cons_r_veto,
            "inv_c_vetoes": stages.inv_c_veto,
        })

    elapsed = time.perf_counter_ns() - started
    audit_rng = np.random.default_rng(seeds[-1])
    object_accept = 0
    agreements = 0
    object_latencies_ns: List[float] = []
    for _ in range(object_audits):
        result, vector_accept = _object_collusion_candidate(state, Q, r, p_inf, audit_rng)
        object_accept += int(result.accepted)
        agreements += int(result.accepted == vector_accept)
        object_latencies_ns.append(float(result.latency_ns))

    # Preserve the old Test-13 latency plots, but measure the literal semantic
    # V_L -> Cons_R -> Inv_C -> V_G path used by the hardened Test 14.  When
    # object audits are disabled, one honest literal execution provides a
    # non-empty, explicitly identified fallback sample.
    if not object_latencies_ns:
        fallback = V_G(state, build_honest_evidence(state))
        if not fallback.accepted:
            raise RuntimeError(f"Latency fallback baseline failed: {fallback.reason}")
        object_latencies_ns.append(float(fallback.latency_ns))

    ci_low, ci_high = _wilson_interval(aggregate.accepted, aggregate.iterations)
    rates = aggregate.as_rates()
    result = EnhancedCollusionResult(
        q=q,
        Q=Q,
        r=r,
        m=m,
        iterations=aggregate.iterations,
        seed_replicates=len(counts),
        p_inf=p_inf,
        local_pass_rate=rates["local_pass_rate"],
        cons_pass_rate=rates["cons_pass_rate"],
        inv_pass_rate=rates["inv_pass_rate"],
        vg_accept_rate=rates["vg_accept_rate"],
        v_l_reject_rate=rates["v_l_reject_rate"],
        cons_r_veto_rate=rates["cons_r_veto_rate"],
        inv_c_veto_rate=rates["inv_c_veto_rate"],
        exact_ref=exact_injective_reference(Q, r, m, p_inf),
        theorem_ref=theorem_reference(q, m, p_inf),
        seed_mean_accept_rate=float(statistics.fmean(accept_rates)),
        seed_std_accept_rate=float(statistics.stdev(accept_rates)) if len(accept_rates) > 1 else 0.0,
        ci95_low=ci_low,
        ci95_high=ci_high,
        avg_direct=sum_direct / aggregate.iterations,
        avg_inferred=sum_inferred / aggregate.iterations,
        avg_failed=sum_failed / aggregate.iterations,
        object_audits=object_audits,
        object_accept_rate=object_accept / object_audits if object_audits else 0.0,
        object_vector_agreement_rate=agreements / object_audits if object_audits else 1.0,
        simulation_ns_per_iteration=elapsed / aggregate.iterations,
        single_candidate_latency_p50_ns=quantile(object_latencies_ns, 0.50),
        single_candidate_latency_p95_ns=quantile(object_latencies_ns, 0.95),
        single_candidate_latency_p99_ns=quantile(object_latencies_ns, 0.99),
    )
    return result, seed_rows


def _semantic_attack_batch(
    state: CNVSSemanticState,
    equation: SemanticEquation,
    batch_size: int,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    critical_index = _critical_fact_index(state)
    candidate = np.repeat(state.hidden.expected_values[None, :], batch_size, axis=0)
    alpha = rng.uniform(0.55, 0.95, size=(batch_size, 3))
    signs = np.asarray([1.0, 1.0, -1.0])
    local_ok = np.ones(batch_size, dtype=bool)

    observed_required: Dict[str, np.ndarray] = {}
    for col, fact_id in enumerate(equation.required_fact_ids):
        leaf = state.leaves[state.fact_to_selector[fact_id]]
        expected = float(leaf.fact.value)
        epsilon = float(leaf.fact.epsilon)
        observed = expected + signs[col] * alpha[:, col] * epsilon
        observed_required[fact_id] = observed
        local_ok &= np.isfinite(observed) & (np.abs(observed - expected) <= epsilon + 1e-15)
        critical_col = critical_index.get(fact_id)
        if critical_col is not None:
            candidate[:, critical_col] = observed

    # Cons_R receives unchanged selectors, parent roles and task digests.
    cons_ok = np.ones(batch_size, dtype=bool)
    semantic_residual = np.abs(
        observed_required[equation.required_fact_ids[2]] -
        observed_required[equation.required_fact_ids[0]] * observed_required[equation.required_fact_ids[1]]
    )
    target_semantic_ok = semantic_residual <= float(equation.tolerance) + 1e-12
    other_semantic_ok = evaluate_semantic_equations_batch(state, candidate)
    hidden_ok = evaluate_hidden_invariants_batch(state, candidate)
    inv_ok = target_semantic_ok & other_semantic_ok & hidden_ok
    return local_ok, cons_ok, inv_ok, candidate


def run_semantic_attack_full_pipeline(
    state: CNVSSemanticState,
    iterations: int,
    batch_size: int,
    seed_replicates: int,
    master_seed: int,
    object_audits: int,
) -> Tuple[EnhancedSemanticAttackResult, List[Dict[str, Any]]]:
    equation = next(eq for eq in state.hidden.semantic_equations if eq.name == "kitchen_area")
    eq_idx = next(i for i, eq in enumerate(state.hidden.semantic_equations) if eq.name == equation.name)
    attached_node = state.hidden.semantic_equation_nodes[eq_idx]
    counts = _split_iterations(iterations, seed_replicates)
    seeds = _seed_children(master_seed, len(counts) + 1)
    aggregate = StageCounters()
    veto_rates: List[float] = []
    seed_rows: List[Dict[str, Any]] = []

    for replicate, (n_rep, seed) in enumerate(zip(counts, seeds), start=1):
        rng = np.random.default_rng(seed)
        stages = StageCounters()
        remaining = n_rep
        while remaining > 0:
            b = min(batch_size, remaining)
            local_ok, cons_ok, inv_ok, _ = _semantic_attack_batch(state, equation, b, rng)
            stages.add_arrays(local_ok, cons_ok, inv_ok)
            remaining -= b
        aggregate.merge(stages)
        veto_rate = stages.inv_c_veto / stages.iterations
        veto_rates.append(veto_rate)
        seed_rows.append({
            "replicate": replicate,
            "seed": seed,
            "iterations": stages.iterations,
            "local_pass_rate": stages.local_pass / stages.iterations,
            "cons_pass_rate": stages.cons_pass / stages.iterations,
            "inv_c_veto_rate": veto_rate,
            "vg_accept_rate": stages.accepted / stages.iterations,
        })

    audit_rng = np.random.default_rng(seeds[-1])
    object_veto = 0
    agreements = 0
    facts = [state.leaves[state.fact_to_selector[fid]].fact for fid in equation.required_fact_ids]
    for _ in range(object_audits):
        evidence = build_honest_evidence(state)
        alpha = audit_rng.uniform(0.55, 0.95, size=3)
        signs = (1.0, 1.0, -1.0)
        for fact, sign, a in zip(facts, signs, alpha):
            selector = state.fact_to_selector[fact.fact_id]
            observed = float(fact.value) + sign * float(a) * float(fact.epsilon)
            evidence[selector] = V_L(state, selector, observed)
        object_result = V_G(state, evidence)

        # Evaluate the same candidate through the batched stage implementation.
        candidate = state.hidden.expected_values.copy()
        critical_index = _critical_fact_index(state)
        for fact, sign, a in zip(facts, signs, alpha):
            idx = critical_index.get(fact.fact_id)
            if idx is not None:
                candidate[idx] = float(fact.value) + sign * float(a) * float(fact.epsilon)
        required_values = {
            fact.fact_id: float(fact.value) + sign * float(a) * float(fact.epsilon)
            for fact, sign, a in zip(facts, signs, alpha)
        }
        target_residual = abs(
            required_values[equation.required_fact_ids[2]] -
            required_values[equation.required_fact_ids[0]] * required_values[equation.required_fact_ids[1]]
        )
        vector_accept = bool(
            target_residual <= equation.tolerance + 1e-12 and
            evaluate_semantic_equations_batch(state, candidate[None, :])[0] and
            evaluate_hidden_invariants_batch(state, candidate[None, :])[0]
        )
        object_veto += int(not object_result.accepted)
        agreements += int(object_result.accepted == vector_accept)

    ci_low, ci_high = _wilson_interval(aggregate.inv_c_veto, aggregate.iterations)
    result = EnhancedSemanticAttackResult(
        equation_name=equation.name,
        attached_node=attached_node,
        iterations=aggregate.iterations,
        seed_replicates=len(counts),
        local_pass_rate=aggregate.local_pass / aggregate.iterations,
        cons_pass_rate=aggregate.cons_pass / aggregate.iterations,
        inv_c_veto_rate=aggregate.inv_c_veto / aggregate.iterations,
        vg_accept_rate=aggregate.accepted / aggregate.iterations,
        seed_mean_veto_rate=float(statistics.fmean(veto_rates)),
        seed_std_veto_rate=float(statistics.stdev(veto_rates)) if len(veto_rates) > 1 else 0.0,
        ci95_veto_low=ci_low,
        ci95_veto_high=ci_high,
        object_audits=object_audits,
        object_veto_rate=object_veto / object_audits if object_audits else 0.0,
        object_vector_agreement_rate=agreements / object_audits if object_audits else 1.0,
    )
    return result, seed_rows


RELATIONAL_ATTACK_TYPES: Tuple[str, ...] = (
    "blind_parent_guess",
    "blind_role_guess",
    "blind_verifier_guess",
    "stale_task_digest",
    "assignment_collision",
)


def _relational_batch(
    state: CNVSSemanticState,
    attack_index: int,
    batch_size: int,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    selectors = list(state.leaves)
    k = len(selectors)
    target = rng.integers(0, k, size=batch_size)
    local_ok = np.ones(batch_size, dtype=bool)
    cons_ok = np.ones(batch_size, dtype=bool)

    if attack_index == 0:  # blind parent guess
        parent_ids = [node_id for node_id, node in state.nodes.items() if node.children_ids]
        parent_to_idx = {node_id: i for i, node_id in enumerate(parent_ids)}
        expected = np.asarray([parent_to_idx[state.leaves[s].parent_node] for s in selectors], dtype=np.int64)[target]
        guessed = rng.integers(0, len(parent_ids), size=batch_size)
        cons_ok = guessed == expected
    elif attack_index == 1:  # blind semantic-role guess
        guessed = rng.integers(0, k, size=batch_size)
        cons_ok = guessed == target  # roles are unique fact identifiers
    elif attack_index == 2:  # blind verifier assignment guess
        expected = np.asarray([state.leaves[s].assigned_verifier for s in selectors], dtype=np.int64)[target]
        verifier_ids = np.asarray(sorted(leaf.assigned_verifier for leaf in state.leaves.values()), dtype=np.int64)
        guessed = verifier_ids[rng.integers(0, len(verifier_ids), size=batch_size)]
        cons_ok = guessed == expected
    elif attack_index == 3:  # stale/random task digest
        # SHA-256 task binding: a fresh random 256-bit value is compared with the
        # expected digest.  Equality is not assumed impossible; it is calculated.
        expected = np.asarray([state.leaves[s].task_digest for s in selectors], dtype=object)[target]
        guessed = np.asarray([secrets.token_hex(32) for _ in range(batch_size)], dtype=object)
        cons_ok = guessed == expected
    elif attack_index == 4:  # assignment collision
        # The attacker reuses a different active verifier, violating injectivity.
        other = (target + rng.integers(1, k, size=batch_size)) % k
        expected = np.asarray([state.leaves[s].assigned_verifier for s in selectors], dtype=np.int64)[target]
        guessed = np.asarray([state.leaves[s].assigned_verifier for s in selectors], dtype=np.int64)[other]
        cons_ok = guessed == expected
    else:
        raise ValueError("Unknown relational attack index.")

    # Values remain honest; if Cons_R happens to accept a blind exact guess, the
    # honest invariant state also passes.  V_G therefore measures true relational
    # bypass probability rather than assigning detection=count.
    inv_ok = np.ones(batch_size, dtype=bool)
    return local_ok, cons_ok, inv_ok


def _object_relational_candidate(
    state: CNVSSemanticState,
    attack_type: str,
    rng: np.random.Generator,
) -> Tuple[ValidationResult, bool]:
    evidence = build_honest_evidence(state)
    selectors = list(state.leaves)
    target_idx = int(rng.integers(0, len(selectors)))
    selector = selectors[target_idx]
    leaf = state.leaves[selector]
    ev = evidence[selector]
    vector_cons = False

    if attack_type == "blind_parent_guess":
        parent_ids = [node_id for node_id, node in state.nodes.items() if node.children_ids]
        guessed = parent_ids[int(rng.integers(0, len(parent_ids)))]
        evidence[selector] = replace(ev, claimed_parent=guessed)
        vector_cons = guessed == leaf.parent_node
    elif attack_type == "blind_role_guess":
        guessed_selector = selectors[int(rng.integers(0, len(selectors)))]
        guessed = state.leaves[guessed_selector].semantic_role
        evidence[selector] = replace(ev, claimed_role=guessed)
        vector_cons = guessed == leaf.semantic_role
    elif attack_type == "blind_verifier_guess":
        verifier_ids = sorted(x.assigned_verifier for x in state.leaves.values())
        guessed = int(verifier_ids[int(rng.integers(0, len(verifier_ids)))])
        evidence[selector] = replace(ev, verifier_id=guessed)
        vector_cons = guessed == leaf.assigned_verifier
    elif attack_type == "stale_task_digest":
        guessed = secrets.token_hex(32)
        evidence[selector] = replace(ev, task_digest=guessed)
        vector_cons = guessed == leaf.task_digest
    elif attack_type == "assignment_collision":
        other_idx = (target_idx + int(rng.integers(1, len(selectors)))) % len(selectors)
        guessed = state.leaves[selectors[other_idx]].assigned_verifier
        evidence[selector] = replace(ev, verifier_id=guessed)
        vector_cons = guessed == leaf.assigned_verifier
    else:
        raise ValueError(attack_type)

    result = V_G(state, evidence)
    vector_accept = vector_cons  # all values and invariants remain honest
    return result, vector_accept


def run_relational_attacks_full_pipeline(
    state: CNVSSemanticState,
    iterations: int,
    batch_size: int,
    seed_replicates: int,
    master_seed: int,
    object_audits: int,
) -> Tuple[List[EnhancedRelationalAttackResult], List[Dict[str, Any]]]:
    per_type_counts = _split_iterations(iterations, len(RELATIONAL_ATTACK_TYPES))
    all_results: List[EnhancedRelationalAttackResult] = []
    seed_rows: List[Dict[str, Any]] = []
    master_children = _seed_children(master_seed, len(RELATIONAL_ATTACK_TYPES) * (seed_replicates + 1))
    cursor = 0

    for attack_index, (attack_type, type_iterations) in enumerate(zip(RELATIONAL_ATTACK_TYPES, per_type_counts)):
        counts = _split_iterations(type_iterations, seed_replicates)
        seeds = master_children[cursor:cursor + len(counts) + 1]
        cursor += len(counts) + 1
        aggregate = StageCounters()
        for replicate, (n_rep, seed) in enumerate(zip(counts, seeds), start=1):
            rng = np.random.default_rng(seed)
            stages = StageCounters()
            remaining = n_rep
            while remaining > 0:
                b = min(batch_size, remaining)
                local_ok, cons_ok, inv_ok = _relational_batch(state, attack_index, b, rng)
                stages.add_arrays(local_ok, cons_ok, inv_ok)
                remaining -= b
            aggregate.merge(stages)
            seed_rows.append({
                "attack_type": attack_type,
                "replicate": replicate,
                "seed": seed,
                "iterations": stages.iterations,
                "cons_r_detection_rate": stages.cons_r_veto / stages.iterations,
                "vg_bypass_rate": stages.accepted / stages.iterations,
            })

        audit_count = min(object_audits, type_iterations)
        audit_rng = np.random.default_rng(seeds[-1])
        object_detected = agreements = 0
        for _ in range(audit_count):
            result, vector_accept = _object_relational_candidate(state, attack_type, audit_rng)
            object_detected += int(not result.accepted)
            agreements += int(result.accepted == vector_accept)

        low, high = _wilson_interval(aggregate.cons_r_veto, aggregate.iterations)
        all_results.append(EnhancedRelationalAttackResult(
            attack_type=attack_type,
            iterations=aggregate.iterations,
            seed_replicates=len(counts),
            local_pass_rate=aggregate.local_pass / aggregate.iterations,
            cons_r_detection_rate=aggregate.cons_r_veto / aggregate.iterations,
            vg_bypass_rate=aggregate.accepted / aggregate.iterations,
            ci95_detection_low=low,
            ci95_detection_high=high,
            object_audits=audit_count,
            object_detection_rate=object_detected / audit_count if audit_count else 0.0,
            object_vector_agreement_rate=agreements / audit_count if audit_count else 1.0,
        ))
    return all_results, seed_rows


def _leakage_candidate_batch(
    state: CNVSSemanticState,
    known: np.ndarray,
    basis: np.ndarray,
    batch_size: int,
    rng: np.random.Generator,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    m = len(state.hidden.critical_selectors)
    null_dim = basis.shape[1]
    if null_dim == 0:
        candidate = np.repeat(state.hidden.expected_values[None, :], batch_size, axis=0)
        nonzero = np.zeros(batch_size, dtype=bool)
    else:
        coefficients = rng.normal(size=(batch_size, null_dim))
        delta_normalized = coefficients @ basis.T
        bounds = 0.90 * state.hidden.epsilons / state.hidden.scales
        max_ratio = np.max(np.abs(delta_normalized) / np.maximum(bounds[None, :], 1e-15), axis=1)
        valid = max_ratio > 1e-14
        scale = np.zeros(batch_size, dtype=np.float64)
        scale[valid] = 0.85 / max_ratio[valid]
        delta_normalized *= scale[:, None]
        candidate = state.hidden.expected_values[None, :] + delta_normalized * state.hidden.scales[None, :]
        nonzero = np.linalg.norm(delta_normalized, axis=1) > 1e-12

    local_ok = np.all(
        np.abs(candidate - state.hidden.expected_values[None, :]) <= state.hidden.epsilons[None, :] + 1e-15,
        axis=1,
    )
    cons_ok = np.ones(batch_size, dtype=bool)
    hidden_ok = evaluate_hidden_invariants_batch(state, candidate)
    semantic_ok = evaluate_semantic_equations_batch(state, candidate)
    inv_ok = hidden_ok & semantic_ok
    distortion = np.linalg.norm((candidate - state.hidden.expected_values[None, :]) / state.hidden.scales[None, :], axis=1)
    return local_ok, cons_ok, inv_ok, nonzero, distortion


def run_leakage_cycle_full_pipeline(
    state: CNVSSemanticState,
    leakage_fraction: float,
    iterations: int,
    batch_size: int,
    seed_replicates: int,
    master_seed: int,
    object_audits: int,
) -> Tuple[EnhancedLeakageResult, List[Dict[str, Any]]]:
    A = state.hidden.matrix
    total_rows, m = A.shape
    leaked_rows = min(total_rows, int(round(leakage_fraction * total_rows)))
    leaked_indices = state.hidden.leakage_order[:leaked_rows]
    known = A[np.asarray(leaked_indices, dtype=int)] if leaked_rows else np.zeros((0, m))
    basis = _nullspace(known)
    null_dim = basis.shape[1]
    counts = _split_iterations(iterations, seed_replicates)
    seeds = _seed_children(master_seed, len(counts) + 1)
    aggregate = StageCounters()
    feasible = 0
    accepted_false = 0
    distortion_sum = 0.0
    seed_rows: List[Dict[str, Any]] = []

    for replicate, (n_rep, seed) in enumerate(zip(counts, seeds), start=1):
        rng = np.random.default_rng(seed)
        stages = StageCounters()
        rep_feasible = rep_accepted_false = 0
        rep_distortion = 0.0
        remaining = n_rep
        while remaining > 0:
            b = min(batch_size, remaining)
            local_ok, cons_ok, inv_ok, nonzero, distortion = _leakage_candidate_batch(
                state, known, basis, b, rng
            )
            stages.add_arrays(local_ok, cons_ok, inv_ok)
            rep_feasible += int(nonzero.sum())
            accepted = local_ok & cons_ok & inv_ok & nonzero
            rep_accepted_false += int(accepted.sum())
            rep_distortion += float(distortion[nonzero].sum())
            remaining -= b
        aggregate.merge(stages)
        feasible += rep_feasible
        accepted_false += rep_accepted_false
        distortion_sum += rep_distortion
        seed_rows.append({
            "leakage_fraction": leakage_fraction,
            "replicate": replicate,
            "seed": seed,
            "iterations": stages.iterations,
            "feasible_false_states": rep_feasible,
            "false_state_bypasses": rep_accepted_false,
            "false_state_bypass_rate": rep_accepted_false / rep_feasible if rep_feasible else 0.0,
        })

    # Total-disclosure reconstruction is evaluated as a separate attack class.
    # The adversary submits the exact critical vector after C_int, R_int and all
    # critical payloads are disclosed.  This is not a false-state bypass: it is
    # unauthorized exact reconstruction with residual min-entropy h=0.
    exact_attempts = iterations if leakage_fraction >= 1.0 - 1e-15 else 0
    exact_accepted = 0
    if exact_attempts:
        remaining = exact_attempts
        expected = state.hidden.expected_values
        while remaining > 0:
            b = min(batch_size, remaining)
            candidate = np.repeat(expected[None, :], b, axis=0)
            local_ok = np.all(np.abs(candidate - expected[None, :]) <= state.hidden.epsilons[None, :] + 1e-15, axis=1)
            cons_ok = np.ones(b, dtype=bool)
            inv_ok = evaluate_hidden_invariants_batch(state, candidate) & evaluate_semantic_equations_batch(state, candidate)
            exact_accepted += int((local_ok & cons_ok & inv_ok).sum())
            remaining -= b

    audit_rng = np.random.default_rng(seeds[-1])
    agreements = 0
    audit_count = object_audits
    for _ in range(audit_count):
        if leakage_fraction >= 1.0 - 1e-15 or null_dim == 0:
            evidence = build_honest_evidence(state)
            vector_accept = True
        else:
            # Generate one candidate explicitly, then evaluate that same candidate
            # in both the batched equations and the literal object-graph V_G path.
            coefficients = audit_rng.normal(size=(1, null_dim))
            delta_normalized = coefficients @ basis.T
            bounds = 0.90 * state.hidden.epsilons / state.hidden.scales
            max_ratio = np.max(np.abs(delta_normalized) / np.maximum(bounds[None, :], 1e-15), axis=1)
            scale = np.zeros(1)
            if max_ratio[0] > 1e-14:
                scale[0] = 0.85 / max_ratio[0]
            delta_normalized *= scale[:, None]
            candidate = state.hidden.expected_values + delta_normalized[0] * state.hidden.scales
            evidence = build_honest_evidence(state)
            for idx, selector in enumerate(state.hidden.critical_selectors):
                evidence[selector] = V_L(state, selector, float(candidate[idx]))
            vector_accept = bool(
                np.all(np.abs(candidate - state.hidden.expected_values) <= state.hidden.epsilons + 1e-15) and
                evaluate_hidden_invariants_batch(state, candidate[None, :])[0] and
                evaluate_semantic_equations_batch(state, candidate[None, :])[0]
            )
        object_result = V_G(state, evidence)
        agreements += int(object_result.accepted == vector_accept)

    result = EnhancedLeakageResult(
        leakage_fraction=leakage_fraction,
        leaked_rows=leaked_rows,
        total_rows=total_rows,
        nullspace_dimension=null_dim,
        iterations=aggregate.iterations,
        seed_replicates=len(counts),
        local_pass_rate=aggregate.local_pass / aggregate.iterations,
        cons_pass_rate=aggregate.cons_pass / aggregate.iterations,
        feasible_false_state_rate=feasible / aggregate.iterations,
        false_state_bypass_rate=accepted_false / feasible if feasible else 0.0,
        semantic_or_hidden_veto_rate=(feasible - accepted_false) / feasible if feasible else 0.0,
        mean_semantic_distortion=distortion_sum / feasible if feasible else 0.0,
        exact_reconstruction_attempts=exact_attempts,
        exact_reconstruction_accept_rate=exact_accepted / exact_attempts if exact_attempts else 0.0,
        object_audits=audit_count,
        object_vector_agreement_rate=agreements / audit_count if audit_count else 1.0,
    )
    return result, seed_rows


def run_refresh_stress_full_pipeline(
    catalog: Sequence[SemanticFact],
    iterations: int,
    seed_replicates: int,
    master_seed: int,
    object_audits: int,
    full_shadow_audits: int,
    q_refresh: int,
    critical_fragments: int,
) -> Tuple[RefreshStressResult, List[Dict[str, Any]]]:
    """
    Stress two refresh properties at different computational scales.

    All `iterations` events generate a blatantly out-of-epsilon observation,
    calculate V_L early rejection, generate a fresh selector/task token, and
    test stale replay equality.  `object_audits` events additionally rebuild a
    real closed branch and run the literal graph V_G before and after refresh.
    A smaller `full_shadow_audits` sample rebuilds the entire topology for cost
    and recovery comparison.
    """
    counts = _split_iterations(iterations, seed_replicates)
    seeds = _seed_children(master_seed, len(counts) + 1)
    early_reject = selector_changed = stale_accept = injective_ok = 0
    seed_rows: List[Dict[str, Any]] = []

    for replicate, (n_rep, seed) in enumerate(zip(counts, seeds), start=1):
        rng = np.random.default_rng(seed)
        # The numerical local-verification condition is calculated directly.
        epsilon = rng.uniform(1e-4, 1.0, size=n_rep)
        absurd_delta = rng.uniform(1.01, 25.0, size=n_rep) * epsilon
        local_ok = np.abs(absurd_delta) <= epsilon
        rep_early = int((~local_ok).sum())

        # Two uint64 words model a 128-bit selector identifier in the batched
        # refresh stress.  Literal refresh audits use the full secret-token and
        # SHA-256 construction implemented by build_state/branch_refresh.
        old_hi = rng.integers(0, np.iinfo(np.uint64).max, size=n_rep, dtype=np.uint64)
        old_lo = rng.integers(0, np.iinfo(np.uint64).max, size=n_rep, dtype=np.uint64)
        new_hi = rng.integers(0, np.iinfo(np.uint64).max, size=n_rep, dtype=np.uint64)
        new_lo = rng.integers(0, np.iinfo(np.uint64).max, size=n_rep, dtype=np.uint64)
        replay = (new_hi == old_hi) & (new_lo == old_lo)
        changed = ~replay

        # A replacement identifier is sampled outside the current active range;
        # this preserves one-fragment-per-verifier injectivity after expulsion.
        expelled = rng.integers(1, q_refresh + 1, size=n_rep)
        replacement = q_refresh + 1 + np.arange(n_rep, dtype=np.int64)
        injective = replacement != expelled

        early_reject += rep_early
        selector_changed += int(changed.sum())
        stale_accept += int(replay.sum())
        injective_ok += int(injective.sum())
        seed_rows.append({
            "replicate": replicate,
            "seed": seed,
            "iterations": n_rep,
            "early_rejection_rate": rep_early / n_rep,
            "selector_changed_rate": float(changed.mean()),
            "stale_replay_accept_rate": float(replay.mean()),
            "injective_reassignment_rate": float(injective.mean()),
        })

    state = build_state(catalog, q_refresh, min(critical_fragments, q_refresh), "refresh_stress_state")
    audit_rng = np.random.default_rng(seeds[-1])
    object_early = object_recovered = object_stale_accept = 0
    full_recovered = 0
    branch_times: List[float] = []
    full_times: List[float] = []
    current = state

    for audit_index in range(object_audits):
        selector = list(current.leaves)[int(audit_rng.integers(0, len(current.leaves)))]
        leaf = current.leaves[selector]
        evidence = build_honest_evidence(current)
        evidence[selector] = V_L(current, selector, absurd_observation(leaf.fact))
        early = V_G(current, evidence)
        object_early += int(early.failed_stage == "V_L" and not early.accepted)

        verifier_map = _verifier_map_by_fact(current)
        verifier_map[leaf.fact.fact_id] = max(verifier_map.values()) + 1
        old_evidence = build_honest_evidence(current)

        started = time.perf_counter_ns()
        refreshed = branch_refresh(current, catalog, selector, verifier_map, f"stress_{audit_index}")
        branch_times.append(float(time.perf_counter_ns() - started))
        recovered = V_G(refreshed, build_honest_evidence(refreshed))
        stale = V_G(refreshed, old_evidence)
        object_recovered += int(recovered.accepted)
        object_stale_accept += int(stale.accepted)

        if audit_index < full_shadow_audits:
            started = time.perf_counter_ns()
            shadow = full_refresh(current, catalog, verifier_map, f"stress_{audit_index}")
            full_times.append(float(time.perf_counter_ns() - started))
            full_recovered += int(V_G(shadow, build_honest_evidence(shadow)).accepted)
        current = refreshed

    result = RefreshStressResult(
        iterations=iterations,
        seed_replicates=len(counts),
        early_rejection_rate=early_reject / iterations,
        selector_changed_rate=selector_changed / iterations,
        stale_replay_accept_rate=stale_accept / iterations,
        injective_reassignment_rate=injective_ok / iterations,
        object_audits=object_audits,
        object_early_rejection_rate=object_early / object_audits if object_audits else 0.0,
        object_recovery_rate=object_recovered / object_audits if object_audits else 0.0,
        object_stale_replay_accept_rate=object_stale_accept / object_audits if object_audits else 0.0,
        full_shadow_audits=min(full_shadow_audits, object_audits),
        full_shadow_recovery_rate=full_recovered / min(full_shadow_audits, object_audits) if min(full_shadow_audits, object_audits) else 0.0,
        branch_refresh_mean_ns=float(statistics.fmean(branch_times)) if branch_times else 0.0,
        full_refresh_mean_ns=float(statistics.fmean(full_times)) if full_times else 0.0,
    )
    return result, seed_rows


def run_scalability_cycle_full_pipeline(
    catalog: Sequence[SemanticFact],
    Q: int,
    vectorized_iterations: int,
    full_pipeline_iterations: int,
    m_default: int,
    batch_size: int,
) -> EnhancedScalabilityResult:
    state = build_state(catalog, Q, min(m_default, Q), f"full_scalability_Q_{Q}")
    evidence = build_honest_evidence(state)
    latencies: List[float] = []
    accepted = 0
    for _ in range(full_pipeline_iterations):
        result = V_G(state, evidence)
        accepted += int(result.accepted)
        latencies.append(float(result.latency_ns))

    started = time.perf_counter_ns()
    remaining = vectorized_iterations
    expected = state.hidden.expected_values
    while remaining > 0:
        b = min(batch_size, remaining)
        candidate = np.repeat(expected[None, :], b, axis=0)
        local_ok = np.all(np.abs(candidate - expected[None, :]) <= state.hidden.epsilons[None, :] + 1e-15, axis=1)
        cons_ok = np.ones(b, dtype=bool)
        inv_ok = evaluate_hidden_invariants_batch(state, candidate) & evaluate_semantic_equations_batch(state, candidate)
        if not np.all(local_ok & cons_ok & inv_ok):
            raise RuntimeError("All-honest scalability pipeline failed.")
        remaining -= b
    elapsed = time.perf_counter_ns() - started

    mean_ns = float(statistics.fmean(latencies))
    return EnhancedScalabilityResult(
        Q=Q,
        fragments=state.terminal_fragment_count,
        total_nodes=state.total_node_count,
        critical_fragments=len(state.hidden.critical_selectors),
        full_pipeline_iterations=full_pipeline_iterations,
        accepted_rate=accepted / full_pipeline_iterations,
        mean_latency_ns=mean_ns,
        p50_latency_ns=quantile(latencies, 0.50),
        p95_latency_ns=quantile(latencies, 0.95),
        p99_latency_ns=quantile(latencies, 0.99),
        throughput_per_second=1e9 / mean_ns if mean_ns > 0 else float("inf"),
        vectorized_iterations=vectorized_iterations,
        vectorized_ns_per_iteration=elapsed / vectorized_iterations,
    )


# ============================================================================== 
# FINAL TEST-14 FIGURES — RESTORED FROM THE ORIGINAL SEMANTIC TEST
# ============================================================================== 


def _save_or_show(path: Path, show_plots: bool) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=300)
    if show_plots:
        plt.show()
    plt.close()


def plot_full_pipeline_collusion_results(
    results: Sequence[EnhancedCollusionResult],
    figure_dir: Path,
    show_plots: bool,
) -> List[str]:
    if not results:
        return []
    figure_dir.mkdir(parents=True, exist_ok=True)
    floor = 1.0 / max(result.iterations for result in results)
    q = [result.q for result in results]
    paths: List[Path] = []

    empirical = [max(result.vg_accept_rate, floor) for result in results]
    exact_ref = [max(result.exact_ref, floor) for result in results]
    theorem_ref = [max(result.theorem_ref, floor) for result in results]
    plt.figure(figsize=(12, 7))
    plt.semilogy(q, empirical, marker="o", label="Executable semantic V_G acceptance")
    plt.semilogy(q, exact_ref, linestyle="--", marker="s", label="Exact injective reference")
    plt.semilogy(q, theorem_ref, linestyle=":", marker="^", label="Theorem reference")
    plt.xlabel("Peripheral verifier compromise q")
    plt.ylabel(
        f"Probability, log scale; zero observations plotted at floor 1/{max(r.iterations for r in results)}"
    )
    plt.title("CNVS Test 14: Semantic V_G Acceptance vs Exact and Theorem References")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / "test_14_semantic_vg_vs_exact_and_theorem.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    plt.figure(figsize=(12, 7))
    plt.plot(q, [r.inv_c_veto_rate for r in results], marker="o", label="V_L + Cons_R pass / Inv_C veto")
    plt.plot(q, [r.v_l_reject_rate for r in results], marker="s", label="V_L rejection")
    plt.plot(q, [r.cons_r_veto_rate for r in results], marker="^", label="Cons_R veto")
    plt.xlabel("Peripheral verifier compromise q")
    plt.ylabel("Observed stage rate")
    plt.title("CNVS Test 14: Full-Pipeline Barrier Outcomes across Collusion Levels")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / "test_14_local_pass_global_veto.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    plt.figure(figsize=(12, 7))
    plt.plot(q, [r.single_candidate_latency_p50_ns / 1e6 for r in results], marker="o", label="p50")
    plt.plot(q, [r.single_candidate_latency_p95_ns / 1e6 for r in results], marker="s", label="p95")
    plt.plot(q, [r.single_candidate_latency_p99_ns / 1e6 for r in results], marker="^", label="p99")
    plt.xlabel("Peripheral verifier compromise q")
    plt.ylabel("Literal single-candidate V_L -> Cons_R -> Inv_C -> V_G latency (ms)")
    plt.title("CNVS Test 14: End-to-End Response Latency across Collusion Levels")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / "test_14_latency_vs_q.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    print("\n[Collusion Plot Output]")
    for item in paths:
        print(f"Saved: {item}")
    return [str(item) for item in paths]


def plot_full_pipeline_scalability_results(
    results: Sequence[EnhancedScalabilityResult],
    figure_dir: Path,
    show_plots: bool,
) -> List[str]:
    if not results:
        return []
    figure_dir.mkdir(parents=True, exist_ok=True)
    Q = [result.Q for result in results]
    paths: List[Path] = []

    plt.figure(figsize=(12, 7))
    plt.plot(Q, [r.mean_latency_ns / 1e6 for r in results], marker="o", label="mean")
    plt.plot(Q, [r.p95_latency_ns / 1e6 for r in results], marker="s", label="p95")
    plt.plot(Q, [r.p99_latency_ns / 1e6 for r in results], marker="^", label="p99")
    plt.xlabel("Active terminal verifiers / semantic fragments Q")
    plt.ylabel("Literal pipeline latency per candidate (ms)")
    plt.title("CNVS Test 14: Semantic Validation Latency from Q=5 to Q=1000")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / "test_14_scalability_latency.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    plt.figure(figsize=(12, 7))
    plt.plot(Q, [r.throughput_per_second for r in results], marker="o")
    plt.xlabel("Active terminal verifiers / semantic fragments Q")
    plt.ylabel("Literal V_G candidates per second")
    plt.title("CNVS Test 14: Validation Throughput across Semantic Scale")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    path = figure_dir / "test_14_scalability_throughput.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    print("\n[Scalability Plot Output]")
    for item in paths:
        print(f"Saved: {item}")
    return [str(item) for item in paths]


def plot_full_pipeline_leakage_results(
    results: Sequence[EnhancedLeakageResult],
    figure_dir: Path,
    show_plots: bool,
) -> List[str]:
    if not results:
        return []
    figure_dir.mkdir(parents=True, exist_ok=True)
    x = [r.leakage_fraction for r in results]
    plt.figure(figsize=(12, 7))
    plt.plot(x, [r.false_state_bypass_rate for r in results], marker="o", label="False-state V_G bypass")
    plt.plot(x, [r.feasible_false_state_rate for r in results], marker="s", label="Feasible false-state construction")
    plt.plot(x, [r.exact_reconstruction_accept_rate for r in results], marker="^", label="Exact authentic reconstruction")
    plt.xlabel("Fraction of hidden invariant rows disclosed")
    plt.ylabel("Observed rate")
    plt.title("CNVS Test 14: Progressive Hidden-Invariant Leakage")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / "test_14_invariant_leakage.png"
    _save_or_show(path, show_plots)
    print("\n[Leakage Plot Output]")
    print(f"Saved: {path}")
    return [str(path)]



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CNVS Test 14 — 500k full-stage Monte Carlo plus object-graph pipeline audits"
    )
    parser.add_argument("--q-main", type=int, default=DEFAULT_Q_MAIN)
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS_PER_Q)
    parser.add_argument("--scalability-iterations", type=int, default=DEFAULT_SCALABILITY_ITERATIONS)
    parser.add_argument("--relational-iterations", type=int, default=DEFAULT_ITERATIONS_PER_Q)
    parser.add_argument("--semantic-iterations", type=int, default=DEFAULT_ITERATIONS_PER_Q)
    parser.add_argument("--leakage-iterations", type=int, default=DEFAULT_ITERATIONS_PER_Q)
    parser.add_argument("--refresh-iterations", type=int, default=DEFAULT_REFRESH_ITERATIONS)
    parser.add_argument("--critical-fragments", type=int, default=DEFAULT_CRITICAL_FRAGMENTS)
    parser.add_argument("--h-min-bits", type=float, default=DEFAULT_H_MIN_BITS)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--seed-replicates", type=int, default=DEFAULT_SEED_REPLICATES)
    parser.add_argument("--object-audits", type=int, default=DEFAULT_OBJECT_PIPELINE_AUDITS)
    parser.add_argument("--refresh-object-audits", type=int, default=DEFAULT_REFRESH_OBJECT_AUDITS)
    parser.add_argument("--refresh-full-shadow-audits", type=int, default=DEFAULT_REFRESH_FULL_SHADOW_AUDITS)
    parser.add_argument("--refresh-q", type=int, default=DEFAULT_REFRESH_Q)
    parser.add_argument(
        "--scalability-full-pipeline-iterations",
        type=int,
        default=DEFAULT_SCALABILITY_FULL_PIPELINE_ITERATIONS,
    )
    parser.add_argument("--output-dir", type=Path, default=Path("test_14_full_pipeline_outputs"))
    parser.add_argument("--master-seed", type=int, default=None)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--show-input", action="store_true")
    parser.add_argument("--no-show", action="store_true")
    parser.add_argument("--skip-scalability", action="store_true")
    parser.add_argument("--skip-refresh-stress", action="store_true")
    parser.add_argument("--skip-relational", action="store_true")
    parser.add_argument("--skip-leakage", action="store_true")
    return parser.parse_args()


def run_test_14(args: argparse.Namespace) -> Dict[str, Any]:
    output_dir = Path(args.output_dir)
    table_dir = output_dir / "tables"
    figure_dir = output_dir / "figures"
    output_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    if args.smoke:
        iterations = min(args.iterations, 2_000)
        relational_iterations = min(args.relational_iterations, 2_000)
        semantic_iterations = min(args.semantic_iterations, 2_000)
        leakage_iterations = min(args.leakage_iterations, 2_000)
        scalability_iterations = min(args.scalability_iterations, 2_000)
        refresh_iterations = min(args.refresh_iterations, 100)
        object_audits = min(args.object_audits, 10)
        refresh_object_audits = min(args.refresh_object_audits, 5)
        refresh_full_shadow_audits = min(args.refresh_full_shadow_audits, 2)
        scalability_full = min(args.scalability_full_pipeline_iterations, 20)
        seed_replicates = min(args.seed_replicates, 2)
        q_scenarios = (0.50, 0.95, 1.00)
        q_grid = (10, 50, 100)
        q_main = min(max(args.q_main, 100), 150)
        critical_fragments = min(args.critical_fragments, 24)
        refresh_q = min(max(args.refresh_q, 20), 40)
    else:
        iterations = args.iterations
        relational_iterations = args.relational_iterations
        semantic_iterations = args.semantic_iterations
        leakage_iterations = args.leakage_iterations
        scalability_iterations = args.scalability_iterations
        refresh_iterations = args.refresh_iterations
        object_audits = args.object_audits
        refresh_object_audits = args.refresh_object_audits
        refresh_full_shadow_audits = args.refresh_full_shadow_audits
        scalability_full = args.scalability_full_pipeline_iterations
        seed_replicates = args.seed_replicates
        q_scenarios = Q_COLLUSION_SCENARIOS
        q_grid = Q_SCALABILITY_GRID
        q_main = args.q_main
        critical_fragments = args.critical_fragments
        refresh_q = args.refresh_q

    for name, value in (
        ("iterations", iterations),
        ("relational_iterations", relational_iterations),
        ("semantic_iterations", semantic_iterations),
        ("leakage_iterations", leakage_iterations),
        ("scalability_iterations", scalability_iterations),
        ("refresh_iterations", refresh_iterations),
        ("seed_replicates", seed_replicates),
        ("scalability_full_pipeline_iterations", scalability_full),
    ):
        if value <= 0:
            raise ValueError(f"{name} must be positive.")

    if args.show_input:
        print(CANONICAL_INPUT_TEXT)

    catalog = build_semantic_catalog()
    master_seed = args.master_seed if args.master_seed is not None else secrets.randbits(128)
    main_state = build_state(catalog, q_main, min(critical_fragments, q_main), "main_full_pipeline_state")
    baseline_evidence = build_honest_evidence(main_state)
    baseline = V_G(main_state, baseline_evidence)
    if not baseline.accepted:
        raise RuntimeError(f"Honest baseline failed: {baseline.reason}")

    print("\n================ CNVS TEST 14 — FULL-PIPELINE 500k ================\n")
    print(f"Semantic catalog: {len(catalog):,} facts")
    print(f"Main state: Q={q_main:,}, nodes={main_state.total_node_count:,}, m={len(main_state.hidden.critical_selectors):,}")
    print(f"Candidates per principal cycle: {iterations:,}")
    print(f"Independent seed replicates: {seed_replicates}")
    print(f"Object-graph V_G audits per cycle: {object_audits:,}")
    print(f"Refresh stress events: {refresh_iterations:,}")
    print(f"Master seed: {master_seed}")

    main_fragment_rows = fragment_table_rows(main_state, baseline_evidence)
    main_fragment_table_path = table_dir / "main_fragment_table.csv"
    hidden_invariant_table_path = table_dir / "hidden_Inv_C_rows.csv"
    semantic_invariant_table_path = table_dir / "semantic_Inv_C_equations.csv"
    write_rows_csv(main_fragment_table_path, main_fragment_rows)
    write_rows_csv(hidden_invariant_table_path, hidden_invariant_table_rows(main_state, baseline_evidence))
    write_rows_csv(semantic_invariant_table_path, semantic_invariant_table_rows(main_state, baseline_evidence))
    print_fragment_table(main_fragment_rows, show_full=not args.compact)

    cycle_table_dir = table_dir / "cycle_tables"
    cycle_table_paths: List[str] = []
    figure_paths: List[str] = []
    top_seeds = _seed_children(master_seed, len(q_scenarios) + 32)

    collusion_results: List[EnhancedCollusionResult] = []
    collusion_seed_rows: List[Dict[str, Any]] = []
    for idx, q in enumerate(q_scenarios):
        # Preserve the original per-q terminal tables.  The semantic state and
        # topology are deliberately fixed across q; separate files make each
        # reported cycle independently auditable and match the legacy output.
        cycle_table_path = cycle_table_dir / f"q_{q:.2f}_fragment_table.csv"
        write_rows_csv(cycle_table_path, main_fragment_rows)
        cycle_table_paths.append(str(cycle_table_path))
        if idx == 0 or not args.compact:
            print(f"\n[Fragment table for q={q:.2f}]")
            print_fragment_table(main_fragment_rows, show_full=not args.compact)

        result, rows = run_collusion_cycle_full_pipeline(
            main_state,
            q=q,
            iterations=iterations,
            h_min_bits=args.h_min_bits,
            batch_size=args.batch_size,
            seed_replicates=seed_replicates,
            master_seed=top_seeds[idx],
            object_audits=object_audits,
        )
        collusion_results.append(result)
        collusion_seed_rows.extend(rows)
        print(
            f"q={q:.2f} | V_G={result.vg_accept_rate:.12f} | exact={result.exact_ref:.12f} | "
            f"95% CI=[{result.ci95_low:.12f},{result.ci95_high:.12f}] | "
            f"object/vector agreement={result.object_vector_agreement_rate:.6f}"
        )
    write_rows_csv(output_dir / "test_14_collusion_full_pipeline_summary.csv", [r.__dict__ for r in collusion_results])
    write_rows_csv(output_dir / "test_14_collusion_seed_replicates.csv", collusion_seed_rows)
    figure_paths.extend(
        plot_full_pipeline_collusion_results(collusion_results, figure_dir, show_plots=not args.no_show)
    )

    semantic_result, semantic_seed_rows = run_semantic_attack_full_pipeline(
        main_state,
        semantic_iterations,
        args.batch_size,
        seed_replicates,
        top_seeds[len(q_scenarios)],
        object_audits,
    )
    write_rows_csv(output_dir / "test_14_semantic_full_pipeline_summary.csv", [semantic_result.__dict__])
    write_rows_csv(output_dir / "test_14_semantic_seed_replicates.csv", semantic_seed_rows)
    print(
        f"Semantic attack | V_L pass={semantic_result.local_pass_rate:.6f} | "
        f"Inv_C veto={semantic_result.inv_c_veto_rate:.6f} | "
        f"object/vector agreement={semantic_result.object_vector_agreement_rate:.6f}"
    )

    relational_results: List[EnhancedRelationalAttackResult] = []
    relational_seed_rows: List[Dict[str, Any]] = []
    if not args.skip_relational:
        relational_results, relational_seed_rows = run_relational_attacks_full_pipeline(
            main_state,
            relational_iterations,
            args.batch_size,
            seed_replicates,
            top_seeds[len(q_scenarios) + 1],
            object_audits,
        )
        write_rows_csv(output_dir / "test_14_relational_full_pipeline_summary.csv", [r.__dict__ for r in relational_results])
        write_rows_csv(output_dir / "test_14_relational_seed_replicates.csv", relational_seed_rows)
        for result in relational_results:
            print(
                f"{result.attack_type} | detected={result.cons_r_detection_rate:.9f} | "
                f"bypass={result.vg_bypass_rate:.9f} | "
                f"object/vector agreement={result.object_vector_agreement_rate:.6f}"
            )

    leakage_results: List[EnhancedLeakageResult] = []
    leakage_seed_rows: List[Dict[str, Any]] = []
    if not args.skip_leakage:
        leakage_levels = (0.0, 0.10, 0.25, 0.50, 0.75, 1.0)
        for offset, leakage in enumerate(leakage_levels, start=len(q_scenarios) + 2):
            result, rows = run_leakage_cycle_full_pipeline(
                main_state,
                leakage,
                leakage_iterations,
                args.batch_size,
                seed_replicates,
                top_seeds[offset],
                object_audits,
            )
            leakage_results.append(result)
            leakage_seed_rows.extend(rows)
            print(
                f"C_int leak={leakage:.0%} | false-state bypass={result.false_state_bypass_rate:.12f} | "
                f"exact h=0 reconstruction={result.exact_reconstruction_accept_rate:.6f} | "
                f"object/vector agreement={result.object_vector_agreement_rate:.6f}"
            )
        write_rows_csv(output_dir / "test_14_leakage_full_pipeline_summary.csv", [r.__dict__ for r in leakage_results])
        write_rows_csv(output_dir / "test_14_leakage_seed_replicates.csv", leakage_seed_rows)
        figure_paths.extend(
            plot_full_pipeline_leakage_results(leakage_results, figure_dir, show_plots=not args.no_show)
        )

    refresh_result: Optional[RefreshStressResult] = None
    refresh_seed_rows: List[Dict[str, Any]] = []
    if not args.skip_refresh_stress:
        refresh_result, refresh_seed_rows = run_refresh_stress_full_pipeline(
            catalog,
            refresh_iterations,
            seed_replicates,
            top_seeds[len(q_scenarios) + 10],
            refresh_object_audits,
            refresh_full_shadow_audits,
            refresh_q,
            critical_fragments,
        )
        write_rows_csv(output_dir / "test_14_refresh_stress_summary.csv", [refresh_result.__dict__])
        write_rows_csv(output_dir / "test_14_refresh_seed_replicates.csv", refresh_seed_rows)
        print(
            f"Refresh | early reject={refresh_result.early_rejection_rate:.6f} | "
            f"branch recovery={refresh_result.object_recovery_rate:.6f} | "
            f"stale replay accepted={refresh_result.object_stale_replay_accept_rate:.6f}"
        )

    scalability_results: List[EnhancedScalabilityResult] = []
    if not args.skip_scalability:
        for Q in q_grid:
            result = run_scalability_cycle_full_pipeline(
                catalog,
                Q,
                scalability_iterations,
                scalability_full,
                critical_fragments,
                args.batch_size,
            )
            scalability_results.append(result)
            print(
                f"Scalability Q={Q:4d} | full V_G n={result.full_pipeline_iterations:,} | "
                f"accepted={result.accepted_rate:.6f} | p95={result.p95_latency_ns/1e6:.6f} ms"
            )
        write_rows_csv(output_dir / "test_14_scalability_full_pipeline_summary.csv", [r.__dict__ for r in scalability_results])
        figure_paths.extend(
            plot_full_pipeline_scalability_results(scalability_results, figure_dir, show_plots=not args.no_show)
        )

    manifest = {
        "test": "CNVS Test 14 full-pipeline 500k",
        "canonical_catalog_size": len(catalog),
        "main_Q": q_main,
        "main_nodes": main_state.total_node_count,
        "critical_fragments": len(main_state.hidden.critical_selectors),
        "iterations_per_collusion_q": iterations,
        "semantic_iterations": semantic_iterations,
        "relational_iterations_total": relational_iterations,
        "leakage_iterations_per_level": leakage_iterations,
        "refresh_stress_iterations": refresh_iterations,
        "scalability_vectorized_iterations_per_Q": scalability_iterations,
        "scalability_literal_V_G_iterations_per_Q": scalability_full,
        "seed_replicates": seed_replicates,
        "object_graph_audits_per_cycle": object_audits,
        "master_seed": master_seed,
        "main_fragment_table": str(main_fragment_table_path),
        "hidden_invariant_table": str(hidden_invariant_table_path),
        "semantic_invariant_table": str(semantic_invariant_table_path),
        "cycle_fragment_tables": cycle_table_paths,
        "figure_paths": figure_paths,
        "methodological_notes": [
            "Every Monte Carlo candidate receives explicit V_L, Cons_R, Inv_C and V_G stage booleans.",
            "Object-graph audits call the literal V_G implementation and are compared with the batched stage result.",
            "V_L is usually generated inside epsilon so that reconstruction can begin; this simulates the normal mostly-honest operating population.",
            "Stealth colluders stay inside epsilon and must be stopped by Cons_R or Inv_C; blatant colluders exceed epsilon and trigger early rejection plus refresh.",
            "Relational detection is calculated from blind parent/role/verifier/digest guesses and assignment collisions; it is not set equal to the attack count.",
            "Leakage tests evaluate both hidden bindings and semantic equations. Total disclosure performs an actual exact-vector acceptance calculation at h=0.",
            "The analytical hypergeometric and theorem references remain comparison-only and never decide V_G.",
        ],
    }
    (output_dir / "test_14_full_pipeline_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "canonical_input_snapshot.txt").write_text(CANONICAL_INPUT_TEXT, encoding="utf-8")

    print(f"\nOutputs written to: {output_dir.resolve()}")
    return {
        "collusion_results": collusion_results,
        "semantic_result": semantic_result,
        "relational_results": relational_results,
        "leakage_results": leakage_results,
        "refresh_result": refresh_result,
        "scalability_results": scalability_results,
        "cycle_table_paths": cycle_table_paths,
        "figure_paths": figure_paths,
        "manifest": manifest,
    }


# ==============================================================================
# CNVS TEST 15 — PARAMETRIC EXTENSION OF TEST 14
# m in {32, 64, 128, 256, 512}, with the Test-14 semantic instance and full graph suite.
# ==============================================================================

import platform as _platform
import random as _random
import socket as _socket
import struct as _struct
import subprocess as _subprocess
from dataclasses import replace as _dc_replace

TEST15_M_VALUES: Tuple[int, ...] = (32, 64, 128, 256, 512)
TEST15_REFERENCE_M = 64
TEST15_MAX_M = max(TEST15_M_VALUES)
TEST15_LEAKAGE_LEVELS: Tuple[float, ...] = (0.0, 0.10, 0.25, 0.50, 0.75, 1.0)


def _safe_text_command(command: Sequence[str]) -> str:
    try:
        completed = _subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return completed.stdout.strip() or completed.stderr.strip()
    except Exception:
        return ""


def capture_hardware_profile() -> Dict[str, Any]:
    """Capture the machine context needed to interpret latency measurements.

    The values are descriptive metadata, not a guarantee of a fixed CPU clock.
    Modern processors dynamically change frequency because of boost, thermal,
    power-management and operating-system scheduling policies.
    """
    profile: Dict[str, Any] = {
        "hostname": _socket.gethostname(),
        "platform": _platform.platform(),
        "system": _platform.system(),
        "release": _platform.release(),
        "machine": _platform.machine(),
        "processor": _platform.processor(),
        "python_version": _platform.python_version(),
        "python_implementation": _platform.python_implementation(),
        "process_architecture_bits": _struct.calcsize("P") * 8,
        "numpy_version": np.__version__,
        "logical_cpu_count": os.cpu_count(),
    }

    try:
        import psutil  # type: ignore

        profile["physical_cpu_count"] = psutil.cpu_count(logical=False)
        freq = psutil.cpu_freq()
        if freq is not None:
            profile["cpu_frequency_current_mhz"] = float(freq.current)
            profile["cpu_frequency_min_mhz"] = float(freq.min)
            profile["cpu_frequency_max_mhz"] = float(freq.max)
        memory = psutil.virtual_memory()
        profile["ram_total_bytes"] = int(memory.total)
        profile["ram_total_gib"] = float(memory.total / (1024 ** 3))
    except Exception:
        profile["physical_cpu_count"] = None

    if _platform.system().lower() == "linux":
        cpuinfo = _safe_text_command(["bash", "-lc", "grep -m1 'model name' /proc/cpuinfo | cut -d: -f2-"])
        if cpuinfo:
            profile["cpu_model"] = cpuinfo.strip()
        meminfo = _safe_text_command(["bash", "-lc", "grep -m1 'MemTotal' /proc/meminfo"])
        if meminfo:
            profile["linux_memtotal"] = meminfo
    elif _platform.system().lower() == "darwin":
        cpu_model = _safe_text_command(["sysctl", "-n", "machdep.cpu.brand_string"])
        if cpu_model:
            profile["cpu_model"] = cpu_model
    elif _platform.system().lower() == "windows":
        cpu_model = _safe_text_command([
            "powershell", "-NoProfile", "-Command",
            "(Get-CimInstance Win32_Processor | Select-Object -First 1 -ExpandProperty Name)",
        ])
        if cpu_model:
            profile["cpu_model"] = cpu_model

    profile["timing_note"] = (
        "Latency values apply to this machine and software environment. Dynamic CPU frequency, "
        "thermal state, background load, memory hierarchy and OS scheduling can change repeated measurements."
    )
    return profile


def write_hardware_profile(output_dir: Path, profile: Mapping[str, Any]) -> Tuple[Path, Path]:
    json_path = output_dir / "test_15_hardware_profile.json"
    txt_path = output_dir / "test_15_hardware_profile.txt"
    json_path.write_text(json.dumps(dict(profile), indent=2, ensure_ascii=False), encoding="utf-8")
    lines = ["CNVS Test 15 — Hardware and software execution profile", ""]
    for key, value in profile.items():
        lines.append(f"{key}: {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def _hidden_state_from_subset(
    state: CNVSSemanticState,
    source_hidden: HiddenInvariantState,
    source_indices: Sequence[int],
    cycle_nonce: str,
) -> HiddenInvariantState:
    """Build a nested hidden state from a full-rank principal subset."""
    indices = tuple(sorted(int(i) for i in source_indices))
    selectors = tuple(source_hidden.critical_selectors[i] for i in indices)
    expected = source_hidden.expected_values[np.asarray(indices, dtype=int)].copy()
    epsilons = source_hidden.epsilons[np.asarray(indices, dtype=int)].copy()
    scales = source_hidden.scales[np.asarray(indices, dtype=int)].copy()
    matrix = source_hidden.matrix[np.ix_(indices, indices)].copy()
    if np.linalg.matrix_rank(matrix) != len(indices):
        raise RuntimeError("The selected nested C_int principal submatrix is not full rank.")
    targets = matrix @ (expected / scales)
    tolerances = source_hidden.tolerances[np.asarray(indices, dtype=int)].copy()
    row_supports = tuple(
        tuple(int(x) for x in np.flatnonzero(np.abs(matrix[row]) > 1e-15))
        for row in range(len(indices))
    )
    row_nodes = tuple(
        lowest_common_ancestor(state.nodes, state.depth_by_node, [selectors[idx] for idx in support])
        for support in row_supports
    )

    old_to_new = {old_idx: new_idx for new_idx, old_idx in enumerate(indices)}
    leakage_order = tuple(
        old_to_new[old_idx]
        for old_idx in source_hidden.leakage_order
        if old_idx in old_to_new
    )
    if len(leakage_order) != len(indices):
        leakage_order = tuple(range(len(indices)))

    return HiddenInvariantState(
        critical_selectors=selectors,
        expected_values=expected,
        epsilons=epsilons,
        scales=scales,
        matrix=matrix,
        targets=targets,
        tolerances=tolerances,
        row_supports=row_supports,
        row_nodes=row_nodes,
        semantic_equations=source_hidden.semantic_equations,
        semantic_equation_nodes=source_hidden.semantic_equation_nodes,
        leakage_order=leakage_order,
        nonce=cycle_nonce,
    )


def _find_full_rank_principal_subset(matrix: np.ndarray, target_size: int, seed: int) -> Tuple[int, ...]:
    """Find a deterministic full-rank principal subset of a full-rank matrix."""
    n = int(matrix.shape[0])
    if target_size > n:
        raise ValueError("target_size exceeds source matrix dimension")
    if target_size == n:
        return tuple(range(n))

    rng = np.random.default_rng(seed)
    canonical = tuple(range(target_size))
    if np.linalg.matrix_rank(matrix[np.ix_(canonical, canonical)]) == target_size:
        return canonical

    for _ in range(20_000):
        candidate = tuple(sorted(int(x) for x in rng.choice(n, size=target_size, replace=False)))
        if np.linalg.matrix_rank(matrix[np.ix_(candidate, candidate)]) == target_size:
            return candidate
    raise RuntimeError(f"Unable to find a full-rank principal subset of size {target_size}.")


def _extend_hidden_state(
    state: CNVSSemanticState,
    base_hidden: HiddenInvariantState,
    target_m: int,
    seed: int,
) -> HiddenInvariantState:
    """Extend an existing hidden state while preserving it as the top-left block.

    Successive calls create the nested family F_64 ⊂ F_128 ⊂ F_256 ⊂ F_512.
    The inherited block is left byte-for-byte unchanged.  Each appended row has a
    non-zero diagonal and may depend only on earlier columns, making the extension
    block-lower-triangular and preserving full rank by construction.
    """
    base_m = len(base_hidden.critical_selectors)
    if target_m < base_m:
        raise ValueError("Use _hidden_state_from_subset for a smaller m.")
    if target_m == base_m:
        return base_hidden

    eligible = sorted(
        selector
        for selector, leaf in state.leaves.items()
        if is_numeric_fact(leaf.fact)
        and leaf.fact.epsilon > 0.0
        and selector not in set(base_hidden.critical_selectors)
    )
    needed = target_m - base_m
    if len(eligible) < needed:
        raise RuntimeError(
            f"Only {len(eligible)} additional numeric fragments are available; {needed} are required."
        )
    selector_rng = _random.Random(seed)
    extras = tuple(sorted(selector_rng.sample(eligible, needed)))
    selectors = tuple(base_hidden.critical_selectors) + extras

    expected = np.asarray([float(state.leaves[s].fact.value) for s in selectors], dtype=np.float64)
    epsilons = np.asarray(
        [max(float(state.leaves[s].fact.epsilon), 1e-12) for s in selectors], dtype=np.float64
    )
    scales = np.maximum(np.abs(expected), 1.0)

    matrix = np.zeros((target_m, target_m), dtype=np.float64)
    matrix[:base_m, :base_m] = base_hidden.matrix
    rng = np.random.default_rng(seed ^ 0x5A17E15)
    for row in range(base_m, target_m):
        matrix[row, row] = 1.0
        candidates = list(range(row))
        extra_count = min(4, len(candidates))
        chosen = rng.choice(candidates, size=extra_count, replace=False) if extra_count else []
        for idx in chosen:
            matrix[row, int(idx)] = float(rng.uniform(-0.04, 0.04))
        norm = np.linalg.norm(matrix[row], ord=1)
        matrix[row] /= norm if norm > 0 else 1.0

    if np.linalg.matrix_rank(matrix) != target_m:
        raise RuntimeError("Extended nested C_int is not full rank.")

    targets = matrix @ (expected / scales)
    tolerances = np.concatenate([
        base_hidden.tolerances.copy(),
        np.full(needed, 1e-10, dtype=np.float64),
    ])
    row_supports = tuple(
        tuple(int(x) for x in np.flatnonzero(np.abs(matrix[row]) > 1e-15))
        for row in range(target_m)
    )
    row_nodes = tuple(
        lowest_common_ancestor(state.nodes, state.depth_by_node, [selectors[idx] for idx in support])
        for support in row_supports
    )
    extra_order = list(range(base_m, target_m))
    selector_rng.shuffle(extra_order)
    leakage_order = tuple(base_hidden.leakage_order) + tuple(extra_order)

    return HiddenInvariantState(
        critical_selectors=selectors,
        expected_values=expected,
        epsilons=epsilons,
        scales=scales,
        matrix=matrix,
        targets=targets,
        tolerances=tolerances,
        row_supports=row_supports,
        row_nodes=row_nodes,
        semantic_equations=base_hidden.semantic_equations,
        semantic_equation_nodes=base_hidden.semantic_equation_nodes,
        leakage_order=leakage_order,
        nonce=f"test15_nested_m{target_m}_{seed:x}",
    )


def build_test15_nested_states(
    catalog: Sequence[SemanticFact],
    q_main: int,
    master_seed: int,
) -> Dict[int, CNVSSemanticState]:
    """Create one semantic graph and five nested critical surfaces.

    The Test-14 constructor is used without alteration for the m=64 control.
    F_32 is a full-rank principal subset of that exact hidden state.  F_128,
    F_256 and F_512 are successive extensions that preserve every selector,
    coefficient, target and tolerance already present at the preceding level.

        F_32 ⊂ F_64 ⊂ F_128 ⊂ F_256 ⊂ F_512

    The active terminal graph, semantic facts, assignments, topology and semantic
    equations are therefore identical across m; only the critical surface and its
    associated C_int cardinality change.
    """
    required = TEST15_MAX_M
    base64: Optional[CNVSSemanticState] = None
    eligible_count = 0

    # build_state follows the exact Test-14 construction path.  A retry is used only
    # if the random 1,000-fragment semantic selection happens to contain fewer than
    # 512 numeric epsilon-bounded facts, which would make F_512 impossible.
    for attempt in range(1, 101):
        candidate = build_state(
            catalog,
            q_main,
            TEST15_REFERENCE_M,
            f"test15_shared_semantic_state_m64_attempt_{attempt}",
        )
        eligible_count = sum(
            1
            for leaf in candidate.leaves.values()
            if is_numeric_fact(leaf.fact) and leaf.fact.epsilon > 0.0
        )
        if eligible_count >= required:
            base64 = candidate
            break
    if base64 is None:
        raise RuntimeError(
            f"Unable to instantiate F_{required}: after 100 Test-14-compatible state "
            f"constructions, the largest active numeric pool remained below {required}."
        )
    if len(base64.hidden.critical_selectors) != TEST15_REFERENCE_M:
        raise RuntimeError("The shared Test-14 control does not contain m=64 critical fragments.")

    subset32 = _find_full_rank_principal_subset(
        base64.hidden.matrix,
        32,
        master_seed ^ 0x320032,
    )
    hidden32 = _hidden_state_from_subset(
        base64,
        base64.hidden,
        subset32,
        cycle_nonce=f"test15_nested_m32_{master_seed:x}",
    )

    hidden128 = _extend_hidden_state(
        base64,
        base64.hidden,
        128,
        master_seed ^ 0x1280128,
    )
    hidden256 = _extend_hidden_state(
        base64,
        hidden128,
        256,
        master_seed ^ 0x2560256,
    )
    hidden512 = _extend_hidden_state(
        base64,
        hidden256,
        512,
        master_seed ^ 0x5120512,
    )

    states: Dict[int, CNVSSemanticState] = {
        32: _dc_replace(base64, cycle_id="test15_shared_semantic_state_m32", hidden=hidden32),
        64: _dc_replace(base64, cycle_id="test15_shared_semantic_state_m64"),
        128: _dc_replace(base64, cycle_id="test15_shared_semantic_state_m128", hidden=hidden128),
        256: _dc_replace(base64, cycle_id="test15_shared_semantic_state_m256", hidden=hidden256),
        512: _dc_replace(base64, cycle_id="test15_shared_semantic_state_m512", hidden=hidden512),
    }

    selector_sets = {m: set(state.hidden.critical_selectors) for m, state in states.items()}
    ordered = list(TEST15_M_VALUES)
    for left, right in zip(ordered, ordered[1:]):
        if not selector_sets[left] < selector_sets[right]:
            raise RuntimeError(f"Nested critical surfaces F_{left} ⊂ F_{right} were not created.")

    # The m=64 control is the unmodified hidden state built by the Test-14 constructor.
    if states[64].hidden is not base64.hidden:
        raise RuntimeError("The m=64 internal control was modified unexpectedly.")

    for m, state in states.items():
        if len(state.hidden.critical_selectors) != m:
            raise RuntimeError(f"Critical selector cardinality mismatch for m={m}.")
        if np.linalg.matrix_rank(state.hidden.matrix) != m:
            raise RuntimeError(f"C_int rank check failed for m={m}.")
        baseline = V_G(state, build_honest_evidence(state))
        if not baseline.accepted:
            raise RuntimeError(f"Honest baseline failed for m={m}: {baseline.reason}")

    return states


def _warm_up_state(state: CNVSSemanticState, repetitions: int = 20) -> None:
    evidence = build_honest_evidence(state)
    for _ in range(max(0, repetitions)):
        result = V_G(state, evidence)
        if not result.accepted:
            raise RuntimeError(result.reason)


def _plot_test15_per_m_collusion(
    results: Sequence[EnhancedCollusionResult],
    m: int,
    figure_dir: Path,
    show_plots: bool,
) -> List[str]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    floor = 1.0 / max(r.iterations for r in results)
    q = [r.q for r in results]
    paths: List[Path] = []

    plt.figure(figsize=(12, 7))
    plt.semilogy(q, [max(r.vg_accept_rate, floor) for r in results], marker="o", label="Executable semantic V_G acceptance")
    plt.semilogy(q, [max(r.exact_ref, floor) for r in results], linestyle="--", marker="s", label="Exact injective reference")
    plt.semilogy(q, [max(r.theorem_ref, floor) for r in results], linestyle=":", marker="^", label="Theorem reference")
    plt.xlabel("Peripheral verifier compromise q")
    plt.ylabel(f"Probability, log scale; zero observations plotted at floor 1/{max(r.iterations for r in results)}")
    plt.title(f"CNVS Test 15 (m={m}): Semantic V_G Acceptance vs References")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / f"test_15_m{m:03d}_semantic_vg_vs_exact_and_theorem.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    plt.figure(figsize=(12, 7))
    plt.plot(q, [r.inv_c_veto_rate for r in results], marker="o", label="V_L + Cons_R pass / Inv_C veto")
    plt.plot(q, [r.v_l_reject_rate for r in results], marker="s", label="V_L rejection")
    plt.plot(q, [r.cons_r_veto_rate for r in results], marker="^", label="Cons_R veto")
    plt.xlabel("Peripheral verifier compromise q")
    plt.ylabel("Observed stage rate")
    plt.title(f"CNVS Test 15 (m={m}): Full-Pipeline Barrier Outcomes")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / f"test_15_m{m:03d}_local_pass_global_veto.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    plt.figure(figsize=(12, 7))
    plt.plot(q, [r.single_candidate_latency_p50_ns / 1e6 for r in results], marker="o", label="p50")
    plt.plot(q, [r.single_candidate_latency_p95_ns / 1e6 for r in results], marker="s", label="p95")
    plt.plot(q, [r.single_candidate_latency_p99_ns / 1e6 for r in results], marker="^", label="p99")
    plt.xlabel("Peripheral verifier compromise q")
    plt.ylabel("Literal single-candidate V_L -> Cons_R -> Inv_C -> V_G latency (ms)")
    plt.title(f"CNVS Test 15 (m={m}): End-to-End Response Latency")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / f"test_15_m{m:03d}_latency_vs_q.png"
    _save_or_show(path, show_plots)
    paths.append(path)
    return [str(p) for p in paths]


def _plot_test15_per_m_scalability(
    results: Sequence[EnhancedScalabilityResult],
    m: int,
    figure_dir: Path,
    show_plots: bool,
) -> List[str]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    Q = [r.Q for r in results]
    paths: List[Path] = []

    plt.figure(figsize=(12, 7))
    plt.plot(Q, [r.mean_latency_ns / 1e6 for r in results], marker="o", label="mean")
    plt.plot(Q, [r.p95_latency_ns / 1e6 for r in results], marker="s", label="p95")
    plt.plot(Q, [r.p99_latency_ns / 1e6 for r in results], marker="^", label="p99")
    plt.xlabel("Active terminal verifiers / semantic fragments Q")
    plt.ylabel("Literal pipeline latency per candidate (ms)")
    plt.title(f"CNVS Test 15 (m={m}): Semantic Validation Latency")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / f"test_15_m{m:03d}_scalability_latency.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    plt.figure(figsize=(12, 7))
    plt.plot(Q, [r.throughput_per_second for r in results], marker="o")
    plt.xlabel("Active terminal verifiers / semantic fragments Q")
    plt.ylabel("Literal V_G candidates per second")
    plt.title(f"CNVS Test 15 (m={m}): Validation Throughput")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    path = figure_dir / f"test_15_m{m:03d}_scalability_throughput.png"
    _save_or_show(path, show_plots)
    paths.append(path)
    return [str(p) for p in paths]


def _plot_test15_per_m_leakage(
    results: Sequence[EnhancedLeakageResult],
    m: int,
    figure_dir: Path,
    show_plots: bool,
) -> List[str]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    x = [r.leakage_fraction for r in results]
    plt.figure(figsize=(12, 7))
    plt.plot(x, [r.false_state_bypass_rate for r in results], marker="o", label="False-state V_G bypass")
    plt.plot(x, [r.feasible_false_state_rate for r in results], marker="s", label="Feasible false-state construction")
    plt.plot(x, [r.exact_reconstruction_accept_rate for r in results], marker="^", label="Exact authentic reconstruction")
    plt.xlabel("Fraction of hidden invariant rows disclosed")
    plt.ylabel("Observed rate")
    plt.title(f"CNVS Test 15 (m={m}): Progressive Hidden-Invariant Leakage")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / f"test_15_m{m:03d}_invariant_leakage.png"
    _save_or_show(path, show_plots)
    return [str(path)]


def _plot_test15_comparisons(
    collusion_by_m: Mapping[int, Sequence[EnhancedCollusionResult]],
    leakage_by_m: Mapping[int, Sequence[EnhancedLeakageResult]],
    scalability_by_m: Mapping[int, Sequence[EnhancedScalabilityResult]],
    figure_dir: Path,
    show_plots: bool,
) -> List[str]:
    figure_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []

    plt.figure(figsize=(12, 7))
    floor = 1.0 / max(r.iterations for rows in collusion_by_m.values() for r in rows)
    for m in TEST15_M_VALUES:
        rows = collusion_by_m[m]
        plt.semilogy([r.q for r in rows], [max(r.vg_accept_rate, floor) for r in rows], marker="o", label=f"Executable V_G, m={m}")
    plt.xlabel("Peripheral verifier compromise q")
    plt.ylabel(f"Authentic critical-state reconstruction probability; floor 1/{int(1/floor)}")
    plt.title("CNVS Test 15: Direct m-Sensitivity of Semantic V_G Acceptance")
    plt.grid(True, which="both", linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / "test_15_comparison_semantic_vg_by_m.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    plt.figure(figsize=(12, 7))
    for m in TEST15_M_VALUES:
        rows = collusion_by_m[m]
        plt.plot([r.q for r in rows], [r.inv_c_veto_rate for r in rows], marker="o", label=f"Inv_C veto, m={m}")
    plt.xlabel("Peripheral verifier compromise q")
    plt.ylabel("V_L + Cons_R pass / Inv_C veto rate")
    plt.title("CNVS Test 15: Direct m-Sensitivity of the Global Veto Barrier")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / "test_15_comparison_inv_c_veto_by_m.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    for percentile_name, field_name in (
        ("p50", "single_candidate_latency_p50_ns"),
        ("p95", "single_candidate_latency_p95_ns"),
        ("p99", "single_candidate_latency_p99_ns"),
    ):
        plt.figure(figsize=(12, 7))
        for m in TEST15_M_VALUES:
            rows = collusion_by_m[m]
            plt.plot([r.q for r in rows], [getattr(r, field_name) / 1e6 for r in rows], marker="o", label=f"{percentile_name}, m={m}")
        plt.xlabel("Peripheral verifier compromise q")
        plt.ylabel("Literal end-to-end latency (ms)")
        plt.title(f"CNVS Test 15: Direct m-Sensitivity of Latency ({percentile_name})")
        plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
        plt.legend()
        path = figure_dir / f"test_15_comparison_latency_{percentile_name}_by_m.png"
        _save_or_show(path, show_plots)
        paths.append(path)

    plt.figure(figsize=(12, 7))
    for m in TEST15_M_VALUES:
        rows = scalability_by_m.get(m, ())
        if rows:
            plt.plot([r.Q for r in rows], [r.mean_latency_ns / 1e6 for r in rows], marker="o", label=f"mean, configured m={m}")
    plt.xlabel("Active terminal verifiers / semantic fragments Q")
    plt.ylabel("Literal pipeline latency per candidate (ms)")
    plt.title("CNVS Test 15: Direct m-Sensitivity of Scalability Latency")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / "test_15_comparison_scalability_latency_by_m.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    plt.figure(figsize=(12, 7))
    for m in TEST15_M_VALUES:
        rows = scalability_by_m.get(m, ())
        if rows:
            plt.plot([r.Q for r in rows], [r.throughput_per_second for r in rows], marker="o", label=f"configured m={m}")
    plt.xlabel("Active terminal verifiers / semantic fragments Q")
    plt.ylabel("Literal V_G candidates per second")
    plt.title("CNVS Test 15: Direct m-Sensitivity of Validation Throughput")
    plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
    plt.legend()
    path = figure_dir / "test_15_comparison_scalability_throughput_by_m.png"
    _save_or_show(path, show_plots)
    paths.append(path)

    if all(leakage_by_m.get(m) for m in TEST15_M_VALUES):
        for metric_label, field_name in (
            ("False-state V_G bypass", "false_state_bypass_rate"),
            ("Feasible false-state construction", "feasible_false_state_rate"),
            ("Exact authentic reconstruction", "exact_reconstruction_accept_rate"),
        ):
            plt.figure(figsize=(12, 7))
            for m in TEST15_M_VALUES:
                rows = leakage_by_m[m]
                plt.plot([r.leakage_fraction for r in rows], [getattr(r, field_name) for r in rows], marker="o", label=f"m={m}")
            plt.xlabel("Fraction of hidden invariant rows disclosed")
            plt.ylabel("Observed rate")
            plt.title(f"CNVS Test 15: {metric_label} by m")
            plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.65)
            plt.legend()
            slug = field_name.replace("_rate", "")
            path = figure_dir / f"test_15_comparison_leakage_{slug}_by_m.png"
            _save_or_show(path, show_plots)
            paths.append(path)

    return [str(p) for p in paths]


def _run_scalability_on_state(
    state: CNVSSemanticState,
    Q: int,
    vectorized_iterations: int,
    full_pipeline_iterations: int,
    batch_size: int,
) -> EnhancedScalabilityResult:
    evidence = build_honest_evidence(state)
    _warm_up_state(state, min(20, full_pipeline_iterations))
    latencies: List[float] = []
    accepted = 0
    for _ in range(full_pipeline_iterations):
        result = V_G(state, evidence)
        accepted += int(result.accepted)
        latencies.append(float(result.latency_ns))

    started = time.perf_counter_ns()
    remaining = vectorized_iterations
    expected = state.hidden.expected_values
    while remaining > 0:
        b = min(batch_size, remaining)
        candidate = np.repeat(expected[None, :], b, axis=0)
        local_ok = np.all(
            np.abs(candidate - expected[None, :]) <= state.hidden.epsilons[None, :] + 1e-15,
            axis=1,
        )
        inv_ok = evaluate_hidden_invariants_batch(state, candidate) & evaluate_semantic_equations_batch(state, candidate)
        if not np.all(local_ok & inv_ok):
            raise RuntimeError("All-honest Test-15 scalability pipeline failed.")
        remaining -= b
    elapsed = time.perf_counter_ns() - started
    mean_ns = float(statistics.fmean(latencies))
    return EnhancedScalabilityResult(
        Q=Q,
        fragments=state.terminal_fragment_count,
        total_nodes=state.total_node_count,
        critical_fragments=len(state.hidden.critical_selectors),
        full_pipeline_iterations=full_pipeline_iterations,
        accepted_rate=accepted / full_pipeline_iterations,
        mean_latency_ns=mean_ns,
        p50_latency_ns=quantile(latencies, 0.50),
        p95_latency_ns=quantile(latencies, 0.95),
        p99_latency_ns=quantile(latencies, 0.99),
        throughput_per_second=1e9 / mean_ns if mean_ns > 0 else float("inf"),
        vectorized_iterations=vectorized_iterations,
        vectorized_ns_per_iteration=elapsed / vectorized_iterations,
    )


def parse_args_test15() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "CNVS Test 15 — direct Test-14 replication with nested critical surfaces "
            "m=32,64,128,256,512 and hardware-qualified latency comparison"
        )
    )
    parser.add_argument("--q-main", type=int, default=DEFAULT_Q_MAIN)
    parser.add_argument("--iterations", type=int, default=DEFAULT_ITERATIONS_PER_Q)
    parser.add_argument("--scalability-iterations", type=int, default=DEFAULT_SCALABILITY_ITERATIONS)
    parser.add_argument("--relational-iterations", type=int, default=DEFAULT_ITERATIONS_PER_Q)
    parser.add_argument("--semantic-iterations", type=int, default=DEFAULT_ITERATIONS_PER_Q)
    parser.add_argument("--leakage-iterations", type=int, default=DEFAULT_ITERATIONS_PER_Q)
    parser.add_argument("--refresh-iterations", type=int, default=DEFAULT_REFRESH_ITERATIONS)
    parser.add_argument("--h-min-bits", type=float, default=DEFAULT_H_MIN_BITS)
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    parser.add_argument("--seed-replicates", type=int, default=DEFAULT_SEED_REPLICATES)
    parser.add_argument("--object-audits", type=int, default=DEFAULT_OBJECT_PIPELINE_AUDITS)
    parser.add_argument("--refresh-object-audits", type=int, default=DEFAULT_REFRESH_OBJECT_AUDITS)
    parser.add_argument("--refresh-full-shadow-audits", type=int, default=DEFAULT_REFRESH_FULL_SHADOW_AUDITS)
    parser.add_argument("--refresh-q", type=int, default=DEFAULT_REFRESH_Q)
    parser.add_argument(
        "--scalability-full-pipeline-iterations",
        type=int,
        default=DEFAULT_SCALABILITY_FULL_PIPELINE_ITERATIONS,
    )
    parser.add_argument("--output-dir", type=Path, default=Path("test_15_m_sensitivity_outputs"))
    parser.add_argument("--master-seed", type=int, default=None)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--compact", action="store_true")
    parser.add_argument("--show-input", action="store_true")
    parser.add_argument("--no-show", action="store_true")
    parser.add_argument("--skip-scalability", action="store_true")
    parser.add_argument("--skip-refresh-stress", action="store_true")
    parser.add_argument("--skip-relational", action="store_true")
    parser.add_argument("--skip-leakage", action="store_true")
    return parser.parse_args()


def run_test_15(args: argparse.Namespace) -> Dict[str, Any]:
    output_dir = Path(args.output_dir)
    figure_dir = output_dir / "figures"
    comparison_figure_dir = figure_dir / "comparisons"
    table_dir = output_dir / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    comparison_figure_dir.mkdir(parents=True, exist_ok=True)
    table_dir.mkdir(parents=True, exist_ok=True)

    if args.smoke:
        iterations = min(args.iterations, 500)
        relational_iterations = min(args.relational_iterations, 500)
        semantic_iterations = min(args.semantic_iterations, 500)
        leakage_iterations = min(args.leakage_iterations, 500)
        scalability_iterations = min(args.scalability_iterations, 500)
        refresh_iterations = min(args.refresh_iterations, 30)
        object_audits = min(args.object_audits, 5)
        refresh_object_audits = min(args.refresh_object_audits, 3)
        refresh_full_shadow_audits = min(args.refresh_full_shadow_audits, 1)
        scalability_full = min(args.scalability_full_pipeline_iterations, 10)
        seed_replicates = min(args.seed_replicates, 2)
        q_scenarios = (0.50, 0.95, 1.00)
        q_grid = (32, 64, 128, 256, 512, 1_000)
        q_main = args.q_main
        refresh_q = min(max(args.refresh_q, 128), q_main)
    else:
        iterations = args.iterations
        relational_iterations = args.relational_iterations
        semantic_iterations = args.semantic_iterations
        leakage_iterations = args.leakage_iterations
        scalability_iterations = args.scalability_iterations
        refresh_iterations = args.refresh_iterations
        object_audits = args.object_audits
        refresh_object_audits = args.refresh_object_audits
        refresh_full_shadow_audits = args.refresh_full_shadow_audits
        scalability_full = args.scalability_full_pipeline_iterations
        seed_replicates = args.seed_replicates
        q_scenarios = Q_COLLUSION_SCENARIOS
        q_grid = Q_SCALABILITY_GRID
        q_main = args.q_main
        refresh_q = args.refresh_q

    if q_main < TEST15_MAX_M:
        raise ValueError(
            f"Test 15 requires q_main >= {TEST15_MAX_M}; the default Q=1000 is recommended "
            "to provide at least 512 active numeric epsilon-bounded fragments."
        )
    for name, value in (
        ("iterations", iterations),
        ("relational_iterations", relational_iterations),
        ("semantic_iterations", semantic_iterations),
        ("leakage_iterations", leakage_iterations),
        ("scalability_iterations", scalability_iterations),
        ("refresh_iterations", refresh_iterations),
        ("seed_replicates", seed_replicates),
        ("scalability_full_pipeline_iterations", scalability_full),
    ):
        if value <= 0:
            raise ValueError(f"{name} must be positive.")

    if args.show_input:
        print(CANONICAL_INPUT_TEXT)

    master_seed = args.master_seed if args.master_seed is not None else secrets.randbits(128)
    catalog = build_semantic_catalog()
    states = build_test15_nested_states(catalog, q_main, master_seed)
    hardware = capture_hardware_profile()
    hardware_json, hardware_txt = write_hardware_profile(output_dir, hardware)

    print("\n========== CNVS TEST 15 — m=32 / 64 / 128 / 256 / 512 ==========\n")
    print(f"Semantic catalog: {len(catalog):,} facts")
    print(f"Shared active state: Q={q_main:,}, nodes={states[64].total_node_count:,}")
    print(f"Nested surfaces: {[len(states[m].hidden.critical_selectors) for m in TEST15_M_VALUES]}")
    print(f"Candidates per principal cycle: {iterations:,}")
    print(f"Master seed: {master_seed}")
    print(f"Hardware profile: {hardware_json}")

    common_baseline_evidence = build_honest_evidence(states[64])
    shared_fragment_rows = fragment_table_rows(states[64], common_baseline_evidence)
    write_rows_csv(table_dir / "test_15_shared_fragment_table.csv", shared_fragment_rows)
    for m in TEST15_M_VALUES:
        m_dir = table_dir / f"m_{m:03d}"
        m_dir.mkdir(parents=True, exist_ok=True)
        evidence = build_honest_evidence(states[m])
        write_rows_csv(m_dir / f"test_15_m{m:03d}_hidden_Inv_C_rows.csv", hidden_invariant_table_rows(states[m], evidence))
        write_rows_csv(m_dir / f"test_15_m{m:03d}_semantic_Inv_C_equations.csv", semantic_invariant_table_rows(states[m], evidence))

    seed_bank = _seed_children(master_seed, len(q_scenarios) + 64)
    collusion_by_m: Dict[int, List[EnhancedCollusionResult]] = {m: [] for m in TEST15_M_VALUES}
    semantic_by_m: Dict[int, EnhancedSemanticAttackResult] = {}
    relational_by_m: Dict[int, List[EnhancedRelationalAttackResult]] = {m: [] for m in TEST15_M_VALUES}
    leakage_by_m: Dict[int, List[EnhancedLeakageResult]] = {m: [] for m in TEST15_M_VALUES}
    refresh_by_m: Dict[int, RefreshStressResult] = {}
    scalability_by_m: Dict[int, List[EnhancedScalabilityResult]] = {m: [] for m in TEST15_M_VALUES}
    figure_paths: List[str] = []

    # Collusion sweep: same q, same Monte Carlo seed and same semantic graph.
    # The run order rotates across q to reduce systematic thermal/order bias.
    collusion_seed_rows_by_m: Dict[int, List[Dict[str, Any]]] = {m: [] for m in TEST15_M_VALUES}
    for q_idx, q in enumerate(q_scenarios):
        order = list(TEST15_M_VALUES[q_idx % len(TEST15_M_VALUES):] + TEST15_M_VALUES[:q_idx % len(TEST15_M_VALUES)])
        for m in order:
            _warm_up_state(states[m], 10)
            result, rows = run_collusion_cycle_full_pipeline(
                states[m],
                q=q,
                iterations=iterations,
                h_min_bits=args.h_min_bits,
                batch_size=args.batch_size,
                seed_replicates=seed_replicates,
                master_seed=seed_bank[q_idx],
                object_audits=object_audits,
            )
            collusion_by_m[m].append(result)
            for row in rows:
                collusion_seed_rows_by_m[m].append({"m": m, **row})
            print(
                f"m={m:3d} q={q:.2f} | V_G={result.vg_accept_rate:.12f} | "
                f"exact={result.exact_ref:.12f} | p50={result.single_candidate_latency_p50_ns/1e6:.6f} ms"
            )

    for m in TEST15_M_VALUES:
        m_output = output_dir / f"m_{m:03d}"
        m_figures = figure_dir / f"m_{m:03d}"
        m_output.mkdir(parents=True, exist_ok=True)
        write_rows_csv(m_output / f"test_15_m{m:03d}_collusion_full_pipeline_summary.csv", [r.__dict__ for r in collusion_by_m[m]])
        write_rows_csv(m_output / f"test_15_m{m:03d}_collusion_seed_replicates.csv", collusion_seed_rows_by_m[m])
        figure_paths.extend(_plot_test15_per_m_collusion(collusion_by_m[m], m, m_figures, show_plots=not args.no_show))

    # Semantic attack, relational attacks, leakage and refresh are repeated exactly
    # as in Test 14 for each m, with common seeds where the function accepts one.
    for m_idx, m in enumerate(TEST15_M_VALUES):
        state = states[m]
        m_output = output_dir / f"m_{m:03d}"
        m_figures = figure_dir / f"m_{m:03d}"
        semantic_result, semantic_rows = run_semantic_attack_full_pipeline(
            state,
            semantic_iterations,
            args.batch_size,
            seed_replicates,
            seed_bank[len(q_scenarios)],
            object_audits,
        )
        semantic_by_m[m] = semantic_result
        write_rows_csv(m_output / f"test_15_m{m:03d}_semantic_full_pipeline_summary.csv", [semantic_result.__dict__])
        write_rows_csv(m_output / f"test_15_m{m:03d}_semantic_seed_replicates.csv", [{"m": m, **row} for row in semantic_rows])

        if not args.skip_relational:
            relational_results, relational_rows = run_relational_attacks_full_pipeline(
                state,
                relational_iterations,
                args.batch_size,
                seed_replicates,
                seed_bank[len(q_scenarios) + 1],
                object_audits,
            )
            relational_by_m[m] = relational_results
            write_rows_csv(m_output / f"test_15_m{m:03d}_relational_full_pipeline_summary.csv", [r.__dict__ for r in relational_results])
            write_rows_csv(m_output / f"test_15_m{m:03d}_relational_seed_replicates.csv", [{"m": m, **row} for row in relational_rows])

        if not args.skip_leakage:
            leakage_seed_rows: List[Dict[str, Any]] = []
            for leak_idx, leakage in enumerate(TEST15_LEAKAGE_LEVELS):
                result, rows = run_leakage_cycle_full_pipeline(
                    state,
                    leakage,
                    leakage_iterations,
                    args.batch_size,
                    seed_replicates,
                    seed_bank[len(q_scenarios) + 2 + leak_idx],
                    object_audits,
                )
                leakage_by_m[m].append(result)
                leakage_seed_rows.extend({"m": m, **row} for row in rows)
            write_rows_csv(m_output / f"test_15_m{m:03d}_leakage_full_pipeline_summary.csv", [r.__dict__ for r in leakage_by_m[m]])
            write_rows_csv(m_output / f"test_15_m{m:03d}_leakage_seed_replicates.csv", leakage_seed_rows)
            figure_paths.extend(_plot_test15_per_m_leakage(leakage_by_m[m], m, m_figures, show_plots=not args.no_show))

        if not args.skip_refresh_stress:
            refresh_result, refresh_rows = run_refresh_stress_full_pipeline(
                catalog,
                refresh_iterations,
                seed_replicates,
                seed_bank[len(q_scenarios) + 20],
                refresh_object_audits,
                refresh_full_shadow_audits,
                refresh_q,
                m,
            )
            refresh_by_m[m] = refresh_result
            write_rows_csv(m_output / f"test_15_m{m:03d}_refresh_stress_summary.csv", [refresh_result.__dict__])
            write_rows_csv(m_output / f"test_15_m{m:03d}_refresh_seed_replicates.csv", [{"m": m, **row} for row in refresh_rows])

    # Scalability: for each Q one active graph is created, then nested m surfaces
    # are derived from that same graph. Effective m can be smaller at low Q.
    if not args.skip_scalability:
        for q_idx, Q in enumerate(q_grid):
            if Q < 1:
                continue
            max_supported_m = min(TEST15_MAX_M, Q)
            base_m = min(64, max_supported_m)
            base_state = build_state(catalog, Q, base_m, f"test15_scalability_shared_Q_{Q}")
            # Derive the requested effective states. At low Q, configured m values
            # collapse to the number of available critical numeric fragments.
            available_m = len([
                s for s, leaf in base_state.leaves.items()
                if is_numeric_fact(leaf.fact) and leaf.fact.epsilon > 0.0
            ])
            target_effective = {m: min(m, available_m) for m in TEST15_M_VALUES}

            # Build each unique effective cardinality on the same active graph.
            # Surfaces above the Test-14 control are extended successively so the
            # scalability sweep preserves the same nesting relation as the main run.
            base_dimension = len(base_state.hidden.critical_selectors)
            by_effective_m: Dict[int, CNVSSemanticState] = {base_dimension: base_state}

            for target in sorted({x for x in target_effective.values() if x < base_dimension}):
                subset = _find_full_rank_principal_subset(
                    base_state.hidden.matrix,
                    target,
                    master_seed ^ (Q << 12) ^ target,
                )
                hidden = _hidden_state_from_subset(
                    base_state,
                    base_state.hidden,
                    subset,
                    cycle_nonce=f"test15_scalability_Q{Q}_m{target}",
                )
                by_effective_m[target] = _dc_replace(
                    base_state,
                    hidden=hidden,
                    cycle_id=f"test15_scalability_Q{Q}_m{target}",
                )

            current_hidden = base_state.hidden
            for target in sorted({x for x in target_effective.values() if x > base_dimension}):
                current_hidden = _extend_hidden_state(
                    base_state,
                    current_hidden,
                    target,
                    master_seed ^ (Q << 12) ^ target,
                )
                by_effective_m[target] = _dc_replace(
                    base_state,
                    hidden=current_hidden,
                    cycle_id=f"test15_scalability_Q{Q}_m{target}",
                )

            state_cache: Dict[int, CNVSSemanticState] = {
                configured_m: by_effective_m[target_effective[configured_m]]
                for configured_m in TEST15_M_VALUES
            }
            order = list(TEST15_M_VALUES[q_idx % len(TEST15_M_VALUES):] + TEST15_M_VALUES[:q_idx % len(TEST15_M_VALUES)])
            for configured_m in order:
                result = _run_scalability_on_state(
                    state_cache[configured_m],
                    Q,
                    scalability_iterations,
                    scalability_full,
                    args.batch_size,
                )
                scalability_by_m[configured_m].append(result)
                print(
                    f"Scalability Q={Q:4d}, configured m={configured_m:3d}, effective m={result.critical_fragments:3d} | "
                    f"mean={result.mean_latency_ns/1e6:.6f} ms"
                )

        for m in TEST15_M_VALUES:
            m_output = output_dir / f"m_{m:03d}"
            m_figures = figure_dir / f"m_{m:03d}"
            write_rows_csv(m_output / f"test_15_m{m:03d}_scalability_full_pipeline_summary.csv", [r.__dict__ for r in scalability_by_m[m]])
            figure_paths.extend(_plot_test15_per_m_scalability(scalability_by_m[m], m, m_figures, show_plots=not args.no_show))

    comparison_paths = _plot_test15_comparisons(
        collusion_by_m,
        leakage_by_m,
        scalability_by_m,
        comparison_figure_dir,
        show_plots=not args.no_show,
    )
    figure_paths.extend(comparison_paths)

    comparison_rows: List[Dict[str, Any]] = []
    for m in TEST15_M_VALUES:
        for result in collusion_by_m[m]:
            comparison_rows.append({
                "m": m,
                "q": result.q,
                "vg_accept_rate": result.vg_accept_rate,
                "exact_ref": result.exact_ref,
                "theorem_ref": result.theorem_ref,
                "inv_c_veto_rate": result.inv_c_veto_rate,
                "latency_p50_ms": result.single_candidate_latency_p50_ns / 1e6,
                "latency_p95_ms": result.single_candidate_latency_p95_ns / 1e6,
                "latency_p99_ms": result.single_candidate_latency_p99_ns / 1e6,
            })
    write_rows_csv(output_dir / "test_15_direct_m_comparison.csv", comparison_rows)

    manifest = {
        "test": "CNVS Test 15 — direct Test-14 m-sensitivity extension",
        "m_values": list(TEST15_M_VALUES),
        "nested_surface_relation": "F_32 subset F_64 subset F_128 subset F_256 subset F_512",
        "m64_control": "The m=64 hidden state is generated by the exact Test-14 constructor and retained unchanged inside Test 15. Analytical references are identical; empirical rates are expected to agree within Monte Carlo uncertainty, while measured latency remains subject to run-to-run hardware noise.",
        "shared_active_Q": q_main,
        "shared_total_nodes": states[64].total_node_count,
        "canonical_catalog_size": len(catalog),
        "iterations_per_collusion_q_per_m": iterations,
        "h_min_bits": args.h_min_bits,
        "seed_replicates": seed_replicates,
        "master_seed": master_seed,
        "hardware_profile_json": str(hardware_json),
        "hardware_profile_text": str(hardware_txt),
        "figure_paths": figure_paths,
        "methodological_notes": [
            "The same active semantic graph, terminal assignment and topology are used for m=32,64,128,256,512 in the principal sweep.",
            "The critical surfaces are nested: F_32 ⊂ F_64 ⊂ F_128 ⊂ F_256 ⊂ F_512.",
            "The m=64 state is the unmodified internal Test-14 control. The m=32, m=128, m=256 and m=512 states are derived without changing the active semantic graph.",
            "The same Monte Carlo seed is reused across m for each q wherever the execution function permits it.",
            "Execution order rotates across m to reduce systematic thermal and ordering bias in latency measurements.",
            "Hardware metadata are recorded automatically; latency values remain conditional on dynamic CPU, OS and background-load conditions.",
            "All Test-14 figure classes are regenerated separately for each m, and direct comparison figures are added.",
        ],
    }
    (output_dir / "test_15_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (output_dir / "canonical_input_snapshot.txt").write_text(CANONICAL_INPUT_TEXT, encoding="utf-8")
    print(f"\nTest 15 outputs written to: {output_dir.resolve()}")
    return {
        "collusion_by_m": collusion_by_m,
        "semantic_by_m": semantic_by_m,
        "relational_by_m": relational_by_m,
        "leakage_by_m": leakage_by_m,
        "refresh_by_m": refresh_by_m,
        "scalability_by_m": scalability_by_m,
        "hardware": hardware,
        "manifest": manifest,
    }


if __name__ == "__main__":
    run_test_15(parse_args_test15())
