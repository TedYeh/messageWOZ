# messageWOZ
Wizard-of-Oz dataset for message passing

* Goal: Build chinese dialogue dataset to control apps(domains) below: 
    1. email
    2. Line
    3. Calendar
 
* Define act and slot from these domains:
* Full ontology for all domains in our data-set. The upper script indicates which domains it belongs to. 
    * *: universal, 1: email, 2: Line, 3: Calendar
    
 | act or slot | item name                                                                 |
 | -------- | ------------------------------------------------------------------------ |
 | act type | inform<sup>\*</sup> / request<sup>\*</sup> / modify<sup>\*</sup> / delete<sup>\*</sup> / select<sup>\*</sup> / not found<sup>\*</sup> / inform sent<sup>12</sup><br> / request senting info<sup>12</sup> / inform builded<sup>3</sup> / REQ_more<sup>\*</sup> / goodbye<sup>\*</sup> |
 | slot     | content<sup>\*</sup> / need cc<sup>1</sup> /receiver<sup>12</sup> / subject<sup>13</sup> / location<sup>3</sup> / is all date<sup>3</sup><br> / event start date<sup>3</sup> / event end date<sup>3</sup> | 

The table below shows the categorical slots, non-categorical slots and intents defined for each domain.
|  Domain  | Categorical slots |                       Non-categorical slots                        | Intents (Actions)|
|:--------:|:-----------------:|:------------------------------------------------------------------:|:----------------:|
|  Gmail   |         -         | receiver, subject, content, copy_receiver, blind_copy_receiver |    find, sent    |
|   Line   |         -         |                         receiver, content                          |    find, sent    |
| Calendar |      all_day      |       subject, content, location, time, start_date, end_date       |   find, build    |
