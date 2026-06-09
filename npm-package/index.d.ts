/**
 * DesignOS - AI-powered design workflow engine for Claude Code, Cursor, and more.
 *
 * @packageDocumentation
 */

/**
 * CLI execution result
 */
export interface CLIResult {
  /** Exit code (0 for success, non-zero for errors) */
  exitCode: number;
  /** Standard output */
  stdout?: string;
  /** Standard error output */
  stderr?: string;
}

/**
 * Installation options for the DesignOS CLI
 */
export interface InstallOptions {
  /** Source directory for local installation */
  localSource?: string;
  /** Target directory for skill installation */
  targetDir?: string;
  /** Skip confirmation prompts */
  skipConfirm?: boolean;
}

/**
 * Available DesignOS skills
 */
export type SkillName =
  | 'uxeval'
  | 'prd2proto'
  | 'ai-analytics'
  | 'ip-design'
  | 'brand-creative'
  | 'design-acceptance';

/**
 * Skill metadata
 */
export interface SkillMetadata {
  /** Skill name */
  name: SkillName;
  /** Skill version */
  version: string;
  /** Skill description */
  description: string;
  /** Installation status */
  installed: boolean;
  /** Skill directory path */
  path?: string;
}

/**
 * UXEval evaluation modes
 */
export type UXEvalMode = 'client' | 'web';

/**
 * UXEval evaluation options
 */
export interface UXEvalOptions {
  /** Evaluation mode */
  mode?: UXEvalMode;
  /** Web URL (required for web mode) */
  url?: string;
  /** Resume interrupted evaluation */
  resume?: boolean;
  /** PRD file path */
  prdPath?: string;
  /** Evaluation scope file path */
  scopePath?: string;
  /** Screenshots directory (for client mode) */
  screenshotsDir?: string;
}

/**
 * Brand creative sub-skills
 */
export type BrandCreativeSubSkill =
  | 'logo-design'
  | 'color-palette'
  | 'typography'
  | 'brand-strategy'
  | 'competitive-analysis'
  | 'visual-identity';

/**
 * Brand creative options
 */
export interface BrandCreativeOptions {
  /** Sub-skill to execute */
  sub?: BrandCreativeSubSkill;
  /** Brand description or brief */
  brief?: string;
}

/**
 * PRD to prototype options
 */
export interface PRD2ProtoOptions {
  /** PRD file path */
  prdPath: string;
  /** Output directory for prototype */
  outputDir?: string;
  /** Prototype framework preference */
  framework?: 'react' | 'vue' | 'html';
}

/**
 * AI analytics options
 */
export interface AIAnalyticsOptions {
  /** Analysis target URL or description */
  target: string;
  /** Analysis type */
  type?: 'competitive' | 'market' | 'user';
}

/**
 * IP design options
 */
export interface IPDesignOptions {
  /** IP character description or brief */
  brief: string;
  /** Design style preference */
  style?: string;
}

/**
 * Design acceptance options
 */
export interface DesignAcceptanceOptions {
  /** Design specification path */
  specPath: string;
  /** Implementation screenshots or URL */
  implementation: string;
  /** Acceptance threshold (0-1) */
  threshold?: number;
}

/**
 * DesignOS project configuration
 */
export interface ProjectConfig {
  /** Project name */
  name: string;
  /** Creation date */
  created: string;
  /** Active skill */
  skill: SkillName;
  /** Evaluation mode (for uxeval) */
  mode?: UXEvalMode;
  /** Additional metadata */
  metadata?: Record<string, unknown>;
}

/**
 * Workspace structure for DesignOS projects
 */
export interface Workspace {
  /** Root directory */
  root: string;
  /** Project configuration */
  config: ProjectConfig;
  /** Inputs directory */
  inputsDir: string;
  /** Outputs directory */
  outputsDir: string;
  /** Runs directory */
  runsDir: string;
}

/**
 * Error types for DesignOS operations
 */
export class DesignOSError extends Error {
  constructor(message: string, code?: string);
  /** Error code */
  code?: string;
}

/**
 * Installation error
 */
export class InstallationError extends DesignOSError {
  constructor(message: string);
}

/**
 * Skill execution error
 */
export class SkillExecutionError extends DesignOSError {
  constructor(message: string, skillName: SkillName);
  /** Skill that failed */
  skillName: SkillName;
}

/**
 * Configuration error
 */
export class ConfigurationError extends DesignOSError {
  constructor(message: string);
}
