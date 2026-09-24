model OccupancySchedule
  output Integer occupants_person;
equation
  occupants_person = if time < 25200 then 0 else if time < 28800 then 2 else if time < 36000 then 8 else if time < 43200 then 12 else if time < 46800 then 4 else if time < 54000 then 15 else if time < 61200 then 10 else if time < 64800 then 3 else 0;
end OccupancySchedule;
