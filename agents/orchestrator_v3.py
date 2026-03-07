"""
Orchestrator V3 - Simplified Self-Repair Architecture
==================================================

This is the NEW simplified orchestrator with:
1. Self-repair loop driven by runtime errors
2. CodeAgent for generation and fixing (with full context)
3. RuntimeRunner for objective validation
4. Simple coordination logic

Architecture:
```
Orchestrator
    ↓
CodeAgent.generate() → files
    ↓
RuntimeRunner.validate() → errors?
    ↓
[Self-repair loop]
    while errors and attempts < MAX:
        CodeAgent.fix(errors) → modified files
        RuntimeRunner.validate() → errors?
    ↓
FrontendAgent (optional)
    ↓
Success
```
"""

import asyncio
import json
from datetime import datetime
from loguru import logger

from domain.entities import (
    AgentType,
    ExecutionResult,
    ExecutionStatus,
    ProjectGenerationResult,
    ProjectConfig,
    Requirement,
    ValidationResult,
    ValidationStatus
)
from infrastructure.llm_provider import OllamaProvider
from infrastructure.file_manager import FileManager

from .code_agent import CodeAgent
from .runtime_runner import RuntimeRunnerOrchestrator
from .frontend_agent import FrontendAgent
from .rollback_agent import RollbackAgent
from .agent_logger import (
    get_logger,
    create_trace,
    log_communication,
    log_execution,
    log_error,
    AgentExecutionContext
)


class OrchestratorV3:
    """
    Simplified Orchestrator with Self-Repair Loop.
    
    Key improvements:
    1. Single agent for generation and fixing (CodeAgent)
    2. Runtime-driven validation (RuntimeRunner)
    3. Self-repair loop with full context
    4. Simplified coordination logic
    """
    
    def __init__(
        self,
        llm_provider: OllamaProvider,
        max_repair_attempts: int = 3,
        generate_frontend: bool = True
    ):
        """
        Initialize the simplified orchestrator.
        
        Args:
            llm_provider: LLM provider for agents
            max_repair_attempts: Maximum attempts for self-repair loop
            generate_frontend: Whether to generate frontend after backend
        """
        self.llm_provider = llm_provider
        self.max_repair_attempts = max_repair_attempts
        self.generate_frontend = generate_frontend
        
        # Single unified agent for code generation and fixing
        self.code_agent = CodeAgent(llm_provider)
        
        # Runtime validation
        self.runtime_runner = None  # Initialized per project
        
        # Frontend agent (optional)
        self.frontend_agent = FrontendAgent(llm_provider)
        
        # Rollback for error recovery
        self.rollback_agent = RollbackAgent()
        
        self.name = "Orchestrator V3"
        logger.info(f"{self.name} initialized")
        logger.info(f"Architecture: CodeAgent → RuntimeRunner → Self-Repair Loop")
        logger.info(f"Max repair attempts: {max_repair_attempts}")
    
    async def execute(self, requirement: Requirement) -> ProjectGenerationResult:
        """
        Execute the full pipeline with self-repair loop.
        
        Args:
            requirement: Project requirements
            
        Returns:
            ProjectGenerationResult with final outcome
        """
        # Initialize logger and trace
        agent_logger = get_logger()
        trace_id = (
            requirement.trace_id
            if hasattr(requirement, 'trace_id') and requirement.trace_id
            else agent_logger.create_trace_id()
        )
        
        agent_logger.log_trace_start(
            trace_id=trace_id,
            metadata={
                "requirement_id": requirement.id,
                "description": requirement.description[:200] if requirement.description else "",
                "output_directory": requirement.project_config.output_directory
            }
        )
        
        start_time = datetime.now()
        result = ProjectGenerationResult()
        result.trace_id = trace_id
        result.add_log(f"Starting generation - Requirement: {requirement.id} - trace_id: {trace_id}")
        
        logger.info("="*60)
        logger.info(f"ORCHESTRATOR V3 - Starting self-repair pipeline - trace_id: {trace_id[:8]}...")
        logger.info("="*60)
        
        try:
            # ==========================================
            # STEP 1: INITIAL CODE GENERATION
            # ==========================================
            logger.info("\n📋 STEP 1: Code Generation")
            result.add_log("STEP 1: Code Generation")
            
            generation_result = await self.code_agent.generate(requirement, trace_id=trace_id)
            
            if not generation_result.success:
                logger.error(f"❌ Initial generation failed: {generation_result.error_message}")
                result.success = False
                result.error_message = f"Generation failed: {generation_result.error_message}"
                return result
            
            result.files_generated.extend(generation_result.files_created)
            logger.info(f"✅ Initial code generated: {len(generation_result.files_created)} files")
            
            # ==========================================
            # STEP 2: RUNTIME VALIDATION + SELF-REPAIR LOOP
            # ==========================================
            logger.info("\n📋 STEP 2: Runtime Validation + Self-Repair Loop")
            result.add_log("STEP 2: Runtime Validation")
            
            project_path = requirement.project_config.output_directory
            self.runtime_runner = RuntimeRunnerOrchestrator(project_path)
            
            # Initialize RuntimeRunner for this project
            self.runtime_runner = RuntimeRunnerOrchestrator(project_path)
            
            # Self-repair loop
            repair_attempt = 0
            all_runtime_errors = []
            
            while repair_attempt < self.max_repair_attempts:
                repair_attempt += 1
                
                logger.info(f"\n--- Self-Repair Loop: Attempt {repair_attempt}/{self.max_repair_attempts} ---")
                result.add_log(f"Self-Repair: Attempt {repair_attempt}")
                
                # Validate with RuntimeRunner
                validation_result = await self.runtime_runner.validate_and_fix()
                
                # Check for errors
                errors = validation_result.get("errors", [])
                failed_services = validation_result.get("failed", 0)
                
                if not errors and failed_services == 0:
                    logger.info("✅ All services validated successfully!")
                    result.add_log("Runtime validation: SUCCESS")
                    break
                
                # Record errors for this attempt
                all_runtime_errors.extend(errors)
                logger.warning(f"⚠️ Validation found {len(errors)} errors (failed: {failed_services} services)")
                
                # Try to fix with CodeAgent (with full context)
                if repair_attempt <= self.max_repair_attempts:
                    logger.info(f"\n📋 STEP 2.{repair_attempt}: CodeAgent fixing errors...")
                    result.add_log(f"CodeAgent fixing: {len(errors)} errors")
                    
                    fix_result = await self.code_agent.fix(
                        requirement=requirement,
                        runtime_errors=errors,
                        attempt=repair_attempt,
                        trace_id=trace_id
                    )
                    
                    if fix_result.success and fix_result.files_modified:
                        result.files_generated.extend(fix_result.files_modified)
                        logger.info(f"✅ Fix applied: {len(fix_result.files_modified)} files modified")
                        result.add_log(f"Fixed: {len(fix_result.files_modified)} files")
                    else:
                        logger.warning(f"⚠️ Fix attempt {repair_attempt} did not modify any files")
                        result.add_log(f"Fix attempt {repair_attempt}: no changes")
                else:
                    logger.warning(f"❌ Max repair attempts ({self.max_repair_attempts}) reached")
            
            # Check if self-repair was successful
            final_validation = await self.runtime_runner.validate_and_fix()
            if final_validation.get("failed", 0) > 0:
                logger.warning(f"⚠️ {final_validation['failed']} services still have issues after {repair_attempt} attempts")
                result.add_log(f"Warning: {final_validation['failed']} services with issues")
            
            # ==========================================
            # STEP 3: FRONTEND GENERATION (optional)
            # ==========================================
            if self.generate_frontend:
                logger.info("\n📋 STEP 3: Frontend Generation")
                result.add_log("STEP 3: Frontend Generation")
                
                frontend_result = await self.frontend_agent.execute(
                    project_path,
                    requirement
                )
                
                if frontend_result.success:
                    result.files_generated.extend(frontend_result.files_created)
                    logger.info(f"✅ Frontend generated: {len(frontend_result.files_created)} files")
                    result.add_log(f"Frontend: {len(frontend_result.files_created)} files")
                else:
                    logger.warning(f"Frontend generation failed: {frontend_result.error_message}")
                    result.add_log(f"Frontend: failed - {frontend_result.error_message}")
            
            # ==========================================
            # SUCCESS
            # ==========================================
            logger.info("\n✅ PIPELINE COMPLETE!")
            result.add_log("Pipeline complete: SUCCESS")
            
            result.success = True
            result.project_path = requirement.project_config.output_directory
            
            # Extract service names
            services = []
            for f in result.files_generated:
                if "/services/" in f:
                    parts = f.split("/services/")
                    if len(parts) > 1:
                        service = parts[1].split("/")[0]
                        if service and service not in services:
                            services.append(service)
            result.services = services
            
            elapsed = (datetime.now() - start_time).total_seconds()
            result.add_log(f"Total time: {elapsed:.2f}s")
            
            logger.info(f"\n🎉 SUCCESS! Generated in {elapsed:.2f}s")
            logger.info(f"📁 Project: {result.project_path}")
            logger.info(f"📝 Services: {result.services}")
            logger.info(f"📄 Files: {len(result.files_generated)}")
            
            return result
            
        except Exception as e:
            logger.exception(f"❌ Fatal error in Orchestrator: {e}")
            result.success = False
            result.error_message = f"Fatal error: {str(e)}"
            result.add_log(f"FATAL ERROR: {str(e)}")
            
            return result
    
    async def execute_with_retry(
        self,
        requirement: Requirement,
        max_retries: int = 3
    ) -> ProjectGenerationResult:
        """
        Execute with retry on failure.
        
        Args:
            requirement: Project requirements
            max_retries: Maximum retry attempts
            
        Returns:
            ProjectGenerationResult
        """
        logger.info(f"Starting execution with {max_retries} retries...")
        
        last_result = None
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"ATTEMPT {attempt}/{max_retries}")
            logger.info(f"{'='*60}")
            
            result = await self.execute(requirement)
            
            if result.success:
                logger.info("✅ Success on attempt!")
                return result
            
            logger.warning(f"❌ Attempt {attempt} failed")
            last_result = result
            
            if attempt < max_retries:
                logger.info("Waiting 2 seconds before retry...")
                await asyncio.sleep(2)
        
        logger.error(f"All {max_retries} attempts failed")
        return last_result
    
    def get_system_status(self) -> dict:
        """Get system status."""
        return {
            "orchestrator": "ready",
            "code_agent": "ready",
            "runtime_runner": "ready",
            "frontend_agent": "ready" if self.generate_frontend else "disabled",
            "llm_connected": self.llm_provider is not None
        }


# Convenience function
def create_orchestrator_v3(llm_provider, **kwargs) -> OrchestratorV3:
    """
    Create an instance of Orchestrator V3.
    
    Args:
        llm_provider: LLM provider
        **kwargs: Additional arguments
        
    Returns:
        OrchestratorV3 instance
    """
    return OrchestratorV3(llm_provider, **kwargs)

