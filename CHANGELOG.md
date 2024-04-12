## 0.3.0 (2024-04-12)

### Feat

- **iam.discover_permissive_policies**: Add new actions

## 0.2.1 (2024-04-10)

### Fix

- **ec2.delete_instances.discover_image_snapshots.exception**: Change image.image_id to image.id
- **ec2.delete_instances.cli**: Revert the original cli interface
- **ec2.delete_instances.discover_image_snapshots**: Skip snapshot retrieval for images not in 'available' state
- **ec2.delete_instances**: Add 'disable_protections' parameter allowing disabling of termination and stop API protections before deletion

## 0.2.0 (2024-04-09)

### Feat

- **ec2.delete_instances**: Add new action
- **ec2.create_images**: Add new action

### Fix

- **ec2.delete_instances**: Uncomment try/except for CLI interface function
- **helpers**: Add format_tags helper for actions that accept tags as parameter

## 0.1.4 (2024-04-08)

### Fix

- **date-handling**: Improve how discover_images and discover_snapshots handle dates
- **validation-logic**: Fix cloudtrail validation logic to correctly evaluate dates

## 0.1.3 (2024-04-08)

### Fix

- **cli**: Add option for tabulated output

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
