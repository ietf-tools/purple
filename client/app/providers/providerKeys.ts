import type { InjectionKey, VNode, Component } from 'vue'

export type Mode = 'overlay' | 'side'

export type OverlayModal = {
  /**
   * Open an overlay modal
   */
  openOverlayModal: (opts: {
    component?: null | VNode | Component
    componentProps?: null | Record<string, unknown>
    mode?: Mode
  }) => Promise<string | undefined>
  /**
 * Close an overlay modal
 */
  closeOverlayModal: () => void
}

/**
 * Overlay modal (injection for Vue)
 */
export const overlayModalKey = Symbol('overlayModalKey') as InjectionKey<OverlayModal>

/**
 * Overlay modal methods for use in modal buttons
 * (injection for Vue)
 */
export const overlayModalMethodsKey = Symbol('overlayModalMethodsKey') as InjectionKey<{
  ok: (val?: string) => void
  cancel: () => void
}>

/**
 * Assign editor FIXME: better description
 * (injection for Vue)
 */
export const assignEditorKey = Symbol('assignEditorKey') as InjectionKey<
(doc: unknown, editor: unknown) => void
>

/**
 * Delete assignment key FIXME: better description
 * (injection for Vue)
 */
export const deleteAssignmentKey = Symbol('deleteAssignmentKey') as InjectionKey<
(assignment: unknown) => void
>
