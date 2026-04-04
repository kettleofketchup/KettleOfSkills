---
last_updated: 2026-03-09
---
# Debugging

## Build & Validate

```bash
# Render and inspect output
kustomize build .

# Pipe to kubectl dry-run for validation
kustomize build . | kubectl apply --dry-run=server -f -

# Diff against live cluster
kustomize build . | kubectl diff -f -

# Build specific overlay
kustomize build overlays/prod

# With Helm chart inflation
kustomize build --enable-helm .
```

## Common Errors

### "accumulating resources"
```
Error: accumulating resources: ... already registered id: ~G_v1_ConfigMap|~X|my-config
```
**Cause**: Same resource (group/version/kind/namespace/name) included twice.
**Fix**: Remove duplicate from `resources` list or ensure unique names. Check if both base and overlay define the same resource.

### "no matches for OriginalId"
```
Error: no matches for OriginalId ... with name: myapp
```
**Cause**: Patch targets a resource not in the resources list.
**Fix**: Verify the resource exists and name/kind match exactly. Check `target` selectors on patches. Remember patches target original names (before namePrefix/nameSuffix).

### "must build at directory"
```
Error: must build at directory: ... not a valid directory
```
**Cause**: Path in `resources` or `components` doesn't exist or doesn't contain kustomization.yaml.
**Fix**: Check relative path resolution. Paths resolve from the kustomization.yaml file location.

### "replacement source not found"
```
Error: replacement source ... not found
```
**Cause**: Source resource in `replacements` doesn't exist in accumulated resources.
**Fix**: Ensure the source ConfigMap/Secret is in `resources` or brought in by a `component`.

### "fieldPath not found"
```
Error: fieldPath ... not found in object
```
**Cause**: The `fieldPath` in replacement source doesn't exist in the source resource.
**Fix**: Check dot-path notation matches actual YAML structure. Array indices are 0-based.

### Replacement target not updating
**Cause**: Target `select` doesn't match any resources.
**Debug**: Build without replacements, verify resource kind/name match selectors exactly.

### Hash suffix breaking references
**Cause**: External system references ConfigMap/Secret by exact name, but generator adds hash.
**Fix**: Set `disableNameSuffixHash: true` in generator options. Or add a `configurations` file to teach kustomize about CRD name reference fields (see [transforms/transformers.md](../transforms/transformers.md#crd-field-configurations)).

## Debugging Tips

### Inspect output
```bash
# Count output resources by kind
kustomize build . | yq '.kind' | sort | uniq -c

# Find specific resource in output
kustomize build . | yq 'select(.kind == "Deployment" and .metadata.name == "myapp")'
```

### Enable origin tracking
Add `buildMetadata` to see where each resource came from:
```yaml
buildMetadata:
  - originAnnotations       # Adds config.kubernetes.io/origin
```

### Compare overlays
```bash
diff <(kustomize build overlays/dev) <(kustomize build overlays/prod)
```

## Build Order

Kustomize processes in this order:
1. Accumulate `resources` (recursively)
2. Apply `components`
3. Run `generators` (ConfigMapGenerator, SecretGenerator)
4. Apply `patches`
5. Apply `transformers` (namespace, namePrefix, labels, images)
6. Apply `replacements`

Key implications:
- Patches target resources by **original** names (before namePrefix/nameSuffix)
- Replacements can reference generator-created resources (generators run first)
- Components merge their patches/transformers into the main kustomization
