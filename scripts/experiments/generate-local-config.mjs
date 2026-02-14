#!/usr/bin/env node

/**
 * Local Config Generator
 *
 * Generates a local development config from the template.
 * This creates experiments.config.js files for local testing.
 *
 * Usage:
 *   node generate-local-config.mjs
 */

import fs from 'fs';
import path from 'path';

const BLOG_TEMPLATE = 'projects/blog/docs/js/statsig/config/experiments.config.template.js';
const BLOG_OUTPUT = 'projects/blog/docs/js/statsig/config/experiments.config.js';

const DEV_TEMPLATE = 'projects/dev/docs/js/statsig/config/experiments.config.template.js';
const DEV_OUTPUT = 'projects/dev/docs/js/statsig/config/experiments.config.js';

/**
 * Copy template to output location
 */
function generateConfig(templatePath, outputPath) {
  try {
    // Check if template exists
    if (!fs.existsSync(templatePath)) {
      console.warn(`⚠️  Template not found: ${templatePath}`);
      return false;
    }

    // Check if output already exists
    if (fs.existsSync(outputPath)) {
      console.log(`ℹ️  Config already exists: ${outputPath}`);
      console.log('   Skipping (delete the file to regenerate)');
      return false;
    }

    // Copy template to output
    const templateContent = fs.readFileSync(templatePath, 'utf8');

    // Ensure output directory exists
    const outputDir = path.dirname(outputPath);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    // Write config file
    fs.writeFileSync(outputPath, templateContent);

    console.log(`✅ Generated: ${outputPath}`);
    return true;
  } catch (error) {
    console.error(`❌ Error generating config: ${error.message}`);
    return false;
  }
}

/**
 * Main execution
 */
function main() {
  console.log('Generating local development configs...\n');

  let success = 0;
  let total = 0;

  // Generate blog config
  total++;
  if (generateConfig(BLOG_TEMPLATE, BLOG_OUTPUT)) {
    success++;
  }

  // Generate dev config (if template exists)
  if (fs.existsSync(DEV_TEMPLATE)) {
    total++;
    if (generateConfig(DEV_TEMPLATE, DEV_OUTPUT)) {
      success++;
    }
  }

  console.log(`\nGenerated ${success}/${total} configs`);

  if (success > 0) {
    console.log('\n📝 Next steps:');
    console.log('   1. Review the generated config files');
    console.log('   2. Update API keys if needed (client keys are safe)');
    console.log('   3. Enable/disable experiments for local testing');
    console.log('   4. Run: mkdocs serve -f projects/blog/mkdocs.yml');
  }

  process.exit(0);
}

main();
