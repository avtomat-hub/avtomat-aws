## 0.1.2 (2024-04-07)

### Fix

- **cli**: Add action descriptions to the parser

## 0.1.1 (2024-04-06)

### Fix

- **validations**: Dummy update to force a version bump

## 0.1.0 (2024-04-06)

### Feat

- **ec2/create_snapshots**: Add new action
- **ec2.discover_volumes**: Add option to filter for root volumes

### Fix

- **pending_limit**: Set the value in DEFAULTS
- **authentication**: Always call set_session and let the helper handle logic whether to create a new session or use a supplied one
- **at_most_one_rule**: Exclude empty lists from evaluated params, [] can be a default value

## 0.0.3 (2024-04-05)

### Fix

- **return-value**: It was misspelt

## 0.0.2 (2024-04-05)

### Fix

- **init**: Initial commit
