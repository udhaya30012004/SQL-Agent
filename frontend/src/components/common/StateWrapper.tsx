import React from 'react';
import { SkeletonLoader } from './SkeletonLoader';
import { ErrorState } from './ErrorState';
import { EmptyState } from './EmptyState';
import { LucideIcon } from 'lucide-react';

interface StateWrapperProps {
  isLoading?: boolean;
  isError?: boolean;
  error?: any;
  isEmpty?: boolean;
  onRetry?: () => void;
  isRetrying?: boolean;
  skeletonVariant?: 'card' | 'table' | 'list' | 'chat' | 'schema';
  skeletonCount?: number;
  emptyTitle?: string;
  emptyDescription?: string;
  emptyIcon?: LucideIcon;
  emptyActionLabel?: string;
  onEmptyAction?: () => void;
  children: React.ReactNode;
  className?: string;
}

export const StateWrapper: React.FC<StateWrapperProps> = ({
  isLoading = false,
  isError = false,
  error,
  isEmpty = false,
  onRetry,
  isRetrying = false,
  skeletonVariant = 'card',
  skeletonCount = 3,
  emptyTitle = 'No data available',
  emptyDescription = 'There are currently no items to display.',
  emptyIcon,
  emptyActionLabel,
  onEmptyAction,
  children,
  className = '',
}) => {
  if (isLoading) {
    return <SkeletonLoader variant={skeletonVariant} count={skeletonCount} className={className} />;
  }

  if (isError) {
    const errorMessage =
      error?.response?.data?.detail || error?.message || 'Failed to load data from server.';
    return (
      <ErrorState
        message={errorMessage}
        onRetry={onRetry}
        isRetrying={isRetrying}
        className={className}
      />
    );
  }

  if (isEmpty) {
    return (
      <EmptyState
        icon={emptyIcon}
        title={emptyTitle}
        description={emptyDescription}
        actionLabel={emptyActionLabel}
        onAction={onEmptyAction}
        className={className}
      />
    );
  }

  return <>{children}</>;
};
