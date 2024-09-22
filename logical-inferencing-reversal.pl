%%========== Spatial rules ==========
% Above and Below Reversal Combine
below(A, B) :- directly_above(B, A).
below(A, B) :- directly_above(B, C), below(A, C).
above(A, B) :- directly_above(A, B).
above(A, B) :- directly_above(A, C), above(C, B).

% Left and Right Reversal Combine
left(A, B) :- directly_right(B, A).
left(A, B) :- directly_right(B, C), left(A, C).
right(A, B) :- directly_right(A, B).
right(A, B) :- directly_right(A, C), right(C, B).

% Ahead
behind(A, B) :- directly_ahead(B, A).
behind(A, B) :- directly_ahead(B, C), behind(A, C).
ahead(A, B) :- directly_ahead(A, B).
ahead(A, B) :- directly_ahead(A, C), ahead(C, B).

% Non-Transitive Relations
% Connected - apply the reverse as well
connected(A, B) :- directly_connected(A, B).
connected(A, B) :- directly_connected(B, A).
% Not Connected - apply the reverse as well
not_connected(A, B) :- \+ connected(A, B).
not_connected(A, B) :- \+ connected(B, A).

%%========== Object defs ==========
% For each object type, define the object by its rules.

%%========== Object defs ==========
% For each object type, define the object by its rules.
% Above
%%==========
% Trees
directly_above(leaves, branches).
directly_above(branches, trunk).
directly_above(trunk, roots).

% Tables
directly_above(tabletop, left_front_leg).
directly_above(tabletop, left_back_leg).
directly_above(tabletop, right_front_leg).
directly_above(tabletop, right_back_leg).

% Boats - doesn't make sense for port or starboard side to be here
directly_above(sail, bow).
directly_above(bow, cabin).
directly_above(cabin, stern).
directly_above(stern, rudder).

% Vehicles

% Chairs

% People

% Right
%%==========
% Trees
directly_right(branches, trunk).

% Tables
directly_right(right_front_leg, left_front_leg).
directly_right(right_back_leg, left_back_leg).
directly_right(right_back_leg, left_front_leg).
directly_right(right_front_leg, left_back_leg).

% Boats
directly_right(starboard_side, port_side).
directly_right(sail, port_side).
directly_right(bow, port_side).
directly_right(cabin, port_side).
directly_right(stern, port_side).
directly_right(starboard_side, sail).
directly_right(starboard_side, bow).
directly_right(starboard_side, cabin).
directly_right(starboard_side, stern).

% Vehicles

% Chairs

% People

% Ahead
%%==========
% Illogical Test
directly_ahead(front, middle).
directly_ahead(middle, back).
directly_ahead(back, front).

% Trees - None

% Tables
directly_ahead(right_front_leg, right_back_leg).
directly_ahead(left_front_leg, left_back_leg).

% Boats
directly_ahead(bow, sail).
directly_ahead(bow, cabin).
directly_ahead(bow, stern).
directly_ahead(bow, rudder).
directly_ahead(sail, rudder).
directly_ahead(cabin, rudder).
directly_ahead(sail, cabin).

% Vehicles

% Chairs

% People

% Connected
%%==========
% Trees
directly_connected(trunk, branches).
directly_connected(roots, trunk).
directly_connected(branches, leaves).

% Tables
directly_connected(left_front_leg, tabletop).
directly_connected(left_back_leg, tabletop).
directly_connected(right_front_leg, tabletop).
directly_connected(right_back_leg, tabletop).

% Boats
directly_connected(rudder, stern).

% Vehicles

% Chairs

% People


%%========== Queries Tested ==========
%% Above/Below Relationships
%?- above(leaves, branches) -- true.
%?- below(branches, right_front_leg) -- false.	Doesn't make sense test
%?- above(tabletop, left_front_leg) -- true.
%?- below(stern, sail) -- true.

% Left/Right Relationships
%?- left(left_front_leg, right_front_leg) -- true.
%?- left(right_back_leg, right_back_leg) -- false.
%?- left(sail, starboard_side) -- true

% Ahead/Behind Relationships
%?- ahead(bow, stern) -- true.
%?- ahead(sail, rudder) -- true.	Transitive Test

% Connected/Not Connected Relationships
%?-connected(leaves, branches) -- true.
%?-connected(branches, leaves) -- true.		Reverse test
%?- not_connected(leaves, rudder) -- true.	Doesn't make sense test
%?- connected(tabletop, right_back_leg) -- true.

%%========== Illogical Queries Tested ==========
% Behind
%?- behind(middle, front) -- true.	Default given
%?- behind(back, front) -- true.	True by transitive, but should conflict with last rule
%?- behind(front, back) -- true.	Illogical, but default given
%?- behind(middle, back) -- true.	Incorrect Illogical - true likely because of transitive rule

%
%?- ahead(front, behind)	-- infinite loops
%?- ahead(back, back)	-- true.	Incorrect
%%========================================