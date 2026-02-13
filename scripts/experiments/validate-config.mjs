#!/usr/bin/env node

/**
 * Statsig Configuration Validator
 *
 * Validates the structure and content of Statsig experiment configurations.
 * Used in CI/CD to catch configuration errors before deployment.
 *
 * Usage:
 *   node validate-config.mjs <config-json-string>
 *   node validate-config.mjs --file <path-to-config.json>
 */

import fs from 'fs';

/**
 * Validate the overall config structure
 */
function validateConfig(config) {
  const errors = [];

  // Validate client configuration
  if (!config.client) {
    errors.push("Missing 'client' configuration");
  } else {
    if (!config.client.apiKey || typeof config.client.apiKey !== 'string') {
      errors.push("Missing or invalid 'client.apiKey'");
    }
    if (!config.client.apiKey?.startsWith('client-')) {
      errors.push("client.apiKey should start with 'client-'");
    }
  }

  // Validate experiments
  if (!config.experiments) {
    errors.push("Missing 'experiments' configuration");
  } else if (typeof config.experiments !== 'object') {
    errors.push("'experiments' must be an object");
  } else {
    // Validate each experiment category
    for (const [category, experiments] of Object.entries(config.experiments)) {
      if (typeof experiments !== 'object') {
        errors.push(`experiments.${category} must be an object`);
        continue;
      }

      // Validate each experiment in the category
      for (const [key, exp] of Object.entries(experiments)) {
        const prefix = `experiments.${category}.${key}`;

        // Required fields
        if (!exp.selector) {
          errors.push(`${prefix}: Missing required field 'selector'`);
        }
        if (!exp.experiment) {
          errors.push(`${prefix}: Missing required field 'experiment'`);
        }
        if (!exp.param) {
          errors.push(`${prefix}: Missing required field 'param'`);
        }
        if (!exp.type) {
          errors.push(`${prefix}: Missing required field 'type'`);
        }

        // Validate type
        const validTypes = ['text', 'attr', 'class'];
        if (exp.type && !validTypes.includes(exp.type)) {
          errors.push(`${prefix}: Invalid type '${exp.type}'. Must be one of: ${validTypes.join(', ')}`);
        }

        // Type-specific validation
        if (exp.type === 'attr' && !exp.attr) {
          errors.push(`${prefix}: type='attr' requires 'attr' field`);
        }
        if (exp.type === 'class' && !exp.className) {
          errors.push(`${prefix}: type='class' requires 'className' field`);
        }

        // Validate priority if present
        if (exp.priority) {
          const validPriorities = ['critical', 'high', 'normal', 'low'];
          if (!validPriorities.includes(exp.priority)) {
            errors.push(`${prefix}: Invalid priority '${exp.priority}'. Must be one of: ${validPriorities.join(', ')}`);
          }
        }

        // Validate pages if present
        if (exp.pages && !Array.isArray(exp.pages)) {
          errors.push(`${prefix}: 'pages' must be an array`);
        }
      }
    }
  }

  // Validate metadata (optional but recommended)
  if (config._meta) {
    if (!config._meta.environment) {
      errors.push("_meta.environment is recommended");
    }
    if (!config._meta.version) {
      errors.push("_meta.version is recommended");
    }
  }

  // Validate tracking config (optional, will be used in Phase 3)
  if (config.tracking) {
    if (config.tracking.clickSelectors && !Array.isArray(config.tracking.clickSelectors)) {
      errors.push("tracking.clickSelectors must be an array");
    }
    if (config.tracking.engagementThresholds) {
      if (config.tracking.engagementThresholds.scrollDepth &&
          !Array.isArray(config.tracking.engagementThresholds.scrollDepth)) {
        errors.push("tracking.engagementThresholds.scrollDepth must be an array");
      }
      if (config.tracking.engagementThresholds.timeOnPage &&
          !Array.isArray(config.tracking.engagementThresholds.timeOnPage)) {
        errors.push("tracking.engagementThresholds.timeOnPage must be an array");
      }
    }
  }

  return errors;
}

/**
 * Count total experiments
 */
function countExperiments(config) {
  if (!config.experiments) return 0;

  let count = 0;
  for (const category of Object.values(config.experiments)) {
    if (typeof category === 'object') {
      count += Object.keys(category).length;
    }
  }
  return count;
}

/**
 * Main execution
 */
function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.error('Usage: node validate-config.mjs <config-json-string>');
    console.error('   or: node validate-config.mjs --file <path-to-config.json>');
    process.exit(1);
  }

  let configJson;

  // Read from file or argument
  if (args[0] === '--file') {
    if (args.length < 2) {
      console.error('Error: --file requires a path argument');
      process.exit(1);
    }
    try {
      configJson = fs.readFileSync(args[1], 'utf8');
    } catch (error) {
      console.error(`Error reading file: ${error.message}`);
      process.exit(1);
    }
  } else {
    configJson = args[0];
  }

  // Parse JSON
  let config;
  try {
    config = JSON.parse(configJson);
  } catch (error) {
    console.error('Error: Invalid JSON');
    console.error(error.message);
    process.exit(1);
  }

  // Validate
  const errors = validateConfig(config);

  if (errors.length === 0) {
    const experimentCount = countExperiments(config);
    console.log('✅ Configuration is valid!');
    console.log(`   Environment: ${config._meta?.environment || 'unknown'}`);
    console.log(`   Version: ${config._meta?.version || 'unknown'}`);
    console.log(`   Experiments: ${experimentCount}`);
    process.exit(0);
  } else {
    console.error('❌ Configuration validation failed:');
    errors.forEach(error => console.error(`   - ${error}`));
    process.exit(1);
  }
}

main();
