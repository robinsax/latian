# latian

Simple home workout tracker with pluggable storage backend and user interface.

This project is intentionally *very* over-engineered, it's also a series of design experiments.

```bash
pip3 install -r requirements.txt

python3 latian                 # Terminal view.
python3 latian -i ws -r multi  # Web view.
```

### Layout

This repository is laid out as follows.

```
latian/
  actions/    Contains application logic
  dal/        Contains the Data Access Layer and underlying storage implementations
  io/         Contains the user I/O provider and underlying source implementations
  model/      Contains the data model
  runtime/    Contains top-level executor implementations
```
